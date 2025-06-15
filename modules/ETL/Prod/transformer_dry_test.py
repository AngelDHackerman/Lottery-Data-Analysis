from botocore.exceptions import ClientError
import pandas as pd
import boto3
import json
import os
import re

# Get the secrets from AWS Secrets Manager
def get_secrets():
    secret_name = "lottery_secret_prod"
    region_name = "us-east-1"

    session = boto3.session.Session()
    client = session.client("secretsmanager", region_name=region_name)

    try:
        response = client.get_secret_value(SecretId=secret_name)
        secret = json.loads(response["SecretString"])
        return {
            "simple": secret["s3_bucket_simple_data_storage_prod_arn"].split(":::")[-1],
            "partitioned": secret["s3_bucket_partitioned_data_storage_prod_arn"].split(":::")[-1]
        }
    except ClientError as e:
        raise RuntimeError(f"Error fetching secrets: {e}")


def list_files_in_s3(bucket_name, prefix):
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    return [content['Key'] for content in response.get('Contents', []) if not content['Key'].endswith("/")]


def download_file_from_s3(bucket_name, s3_key, local_path):
    s3 = boto3.client('s3')
    s3.download_file(bucket_name, s3_key, local_path)
    print(f"Downloaded {s3_key} to {local_path}")


def split_header_body(content_lines):
    content_cleaned = [line.strip() for line in content_lines if line.strip()]
    try:
        header_start = content_cleaned.index("HEADER")
        body_start = content_cleaned.index("BODY")
    except ValueError:
        raise ValueError("The file does not contain expected HEADER or BODY sections.")
    return content_cleaned[header_start + 1: body_start], content_cleaned[body_start + 1:]


def process_header(header):
    try:
        numero_sorteo = re.search(r"NO. (\d+)", header[0]).group(1)
        tipo_sorteo = re.search(r"SORTEO (\w+)", header[0], re.IGNORECASE).group(1)
        fecha_sorteo = re.search(r"FECHA DEL SORTEO: ([\d/]+)", " ".join(header)).group(1)
        fecha_caducidad = re.search(r"FECHA DE CADUCIDAD: ([\d/]+)", " ".join(header)).group(1)
        premios = re.search(r"PRIMER PREMIO (\d+) \|\|\| SEGUNDO PREMIO (\d+) \|\|\| TERCER PREMIO (\d+)", " ".join(header))
        primer_premio, segundo_premio, tercer_premio = premios.groups()
        reintegros = re.search(r"REINTEGROS ([\d, ]+)", " ".join(header)).group(1).replace(" ", "")
    except AttributeError as e:
        raise ValueError("The HEADER does not contain the expected format.") from e

    return {
        "numero_sorteo": int(numero_sorteo),
        "tipo_sorteo": tipo_sorteo,
        "fecha_sorteo": fecha_sorteo,
        "fecha_caducidad": fecha_caducidad,
        "primer_premio": int(primer_premio),
        "segundo_premio": int(segundo_premio),
        "tercer_premio": int(tercer_premio),
        "reintegros": reintegros
    }


def process_body(body):
    premios_data = []
    last_premio_index = None
    for line in body:
        line = line.strip()
        if not line:
            continue
        match = re.match(r"(\d+)\s+(\w+)\s+\.+\s+([\d,]+\.?\d*)", line)
        if match:
            numero_premiado, letras, monto = match.groups()
            monto = float(monto.replace(",", ""))
            premios_data.append({
                "numero_premiado": numero_premiado,
                "letras": letras,
                "monto": monto,
                "vendido_por": None,
                "ciudad": None,
                "departamento": None
            })
            last_premio_index = len(premios_data) - 1
        elif "VENDIDO POR" in line and last_premio_index is not None:
            current_vendedor = line.split("VENDIDO POR", 1)[1].strip()
            premios_data[last_premio_index]["vendido_por"] = current_vendedor
        elif "NO VENDIDO" in line and last_premio_index is not None:
            premios_data[last_premio_index]["vendido_por"] = "NO VENDIDO"
    return premios_data


def split_vendido_por_column(df):
    split_data = df['vendido_por'].str.split(r',', expand=True)
    df['vendedor'] = split_data[0].str.strip()
    df['ciudad'] = split_data[1].str.strip() if split_data.shape[1] > 1 else None
    df['departamento'] = split_data[2].str.strip() if split_data.shape[1] > 2 else None
    df.drop(columns=['vendido_por'], inplace=True)
    return df


def transform():
    secrets = get_secrets()
    bucket_name = secrets['partitioned']
    raw_prefix = "raw/"
    processed_prefix = "processed/"

    raw_files = list_files_in_s3(bucket_name, raw_prefix)
    print(f"Found {len(raw_files)} raw files in S3.")

    for raw_file in raw_files:
        local_tmp_dir = "./temp_files/"
        os.makedirs(local_tmp_dir, exist_ok=True)
        local_path = os.path.join(local_tmp_dir, os.path.basename(raw_file))

        download_file_from_s3(bucket_name, raw_file, local_path)

        with open(local_path, "r", encoding="utf-8") as file:
            file_content = file.read()

        header, body = split_header_body(file_content.splitlines())
        sorteos = [process_header(header)]
        premios = process_body(body)

        for premio in premios:
            premio["numero_sorteo"] = sorteos[0]["numero_sorteo"]

        sorteos_df = pd.DataFrame(sorteos)
        premios_df = pd.DataFrame(premios)
        premios_df = split_vendido_por_column(premios_df)
        premios_df.loc[premios_df['ciudad'].str.upper() == "DE ESTA CAPITAL", 'departamento'] = "GUATEMALA"

        # Clean and types
        premios_df.replace({"N/A": None, "n/a": None, "": None}, inplace=True)
        premios_df['numero_sorteo'] = pd.to_numeric(premios_df['numero_sorteo'], errors='coerce').fillna(0).astype(int)
        premios_df['numero_premiado'] = premios_df['numero_premiado'].astype(str)
        premios_df['letras'] = premios_df['letras'].astype(str)
        premios_df['monto'] = pd.to_numeric(premios_df['monto'], errors='coerce').fillna(0.0).astype(float)

        sorteos_df[['reintegro_primer_premio', 'reintegro_segundo_premio', 'reintegro_tercer_premio']] = sorteos_df['reintegros'].str.split(',', expand=True)
        sorteos_df.drop(columns=['reintegros'], inplace=True)

        numero_sorteo = sorteos_df['numero_sorteo'].iloc[0]
        fecha_sorteo = pd.to_datetime(sorteos_df["fecha_sorteo"].iloc[0], format='%d/%m/%Y', errors='coerce')
        year = fecha_sorteo.year if not pd.isna(fecha_sorteo) else "unknown"

        sorteos_df['year'] = year
        sorteos_df['sorteo'] = numero_sorteo
        premios_df['year'] = year
        premios_df['sorteo'] = numero_sorteo

        # Save to both buckets
        simple_bucket = secrets['simple']
        partitioned_bucket = secrets['partitioned']

        sorteos_df.to_parquet(f"s3://{simple_bucket}/processed/sorteos_{numero_sorteo}.parquet", index=False)
        premios_df.to_parquet(f"s3://{simple_bucket}/processed/premios_{numero_sorteo}.parquet", index=False)

        sorteos_df.to_parquet(f"s3://{partitioned_bucket}/processed/sorteos/", partition_cols=["year", "sorteo"])
        premios_df.to_parquet(f"s3://{partitioned_bucket}/processed/premios/", partition_cols=["year", "sorteo"])

        print(f"✅ Sorteo {numero_sorteo} transformado y subido a S3.")


if __name__ == "__main__":
    transform()
