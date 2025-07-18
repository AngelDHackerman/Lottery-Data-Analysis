from botocore.exceptions import ClientError
from urllib.parse import urlparse
import pandas as pd
import boto3
import json
import csv
import os
import re

# Get the secret from AWS Secrets Manager
def get_secrets():

    secret_name = "lottery_secret_prod_2"
    region_name = "us-east-1"
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        response = client.get_secret_value(SecretId=secret_name)
        secret = json.loads(response["SecretString"])
        return {
            "simple": secret["s3_bucket_simple_data_storage_prod_arn"].split(":::")[-1],
            "partitioned": secret["s3_bucket_partitioned_data_storage_prod_arn"].split(":::")[-1]
        }
    except ClientError as e:
        raise RuntimeError(f"Error fetching secrets: {e}")
    

def process_body(body):
    """
    Processes the BODY section and extracts relevant fields.
    Args:
        body (list): List of lines in the BODY section.
    Returns:
        list: List of dictionaries with processed premios data, including reintegros.
    """
    premios_data = []
    last_premio_index = None  # Índice del último premio procesado

    print("Processing BODY:")  # Que hace este codigo? 
    for line in body:
        line = line.strip()
        if not line:
            continue

        print(f"Processing line: {line}")
        
        # Intentar coincidir con una línea de premio
        match = re.match(r"(\d+)\s+(\w+)\s+\.+\s+([\d,]+\.?\d*)", line)
        if match:
            numero_premiado, letras, monto = match.groups()
            monto = float(monto.replace(",", ""))  # Limpiar el monto
            # reintegro = int(numero_premiado[-1]) # Extract the last digit
            
            premios_data.append({
                "numero_premiado": numero_premiado,
                "letras": letras,
                "monto": monto,
                # "reintegro": reintegro, # Add reintegro column
                "vendido_por": None,  # Default Value to None
                "ciudad": None,       
                "departamento": None  
            })
            last_premio_index = len(premios_data) - 1  # Guarda el índice actual

        elif "VENDIDO POR" in line and last_premio_index is not None:
            # Si encontramos "VENDIDO POR", asignar al último premio
            current_vendedor = line.split("VENDIDO POR", 1)[1].strip()
            premios_data[last_premio_index]["vendido_por"] = current_vendedor

        elif "NO VENDIDO" in line and last_premio_index is not None:
            # Asignar "NO VENDIDO" con valores predeterminados
            premios_data[last_premio_index]["vendido_por"] = "NO VENDIDO" 
            premios_data[last_premio_index]["ciudad"] = None # Adding "None" for compatilibility with SQL 
            premios_data[last_premio_index]["departamento"] = None

        else:
            # Ignorar las líneas que no coinciden (para depuración)
            print(f"Ignored line: {line}")

    print(f"Premios processed: {len(premios_data)}")
    return premios_data


def split_vendido_por_column(df):
    """
    Splits the 'vendido_por' column into 'vendedor', 'ciudad', and 'departamento'.
    Args:
        df (pd.DataFrame): DataFrame with 'vendido_por' column.
    Returns:
        pd.DataFrame: DataFrame with new columns and 'vendido_por' removed.
    """
    split_data = df['vendido_por'].str.split(r',', expand=True) # separates the info by using ","
    df['vendedor'] = split_data[0].str.strip()  # Extract vendor name
    df['ciudad'] = split_data[1].str.strip() if split_data.shape[1] > 1 else None  # Extract city
    df['departamento'] = split_data[2].str.strip() if split_data.shape[1] > 2 else None  # Extract department
    df.drop(columns=['vendido_por'], inplace=True)  # Remove original column
    return df


def transform(bucket_name, raw_prefix, processed_prefix):
    """
    Transforms raw lottery data stored in S3 and uploads processed apache Parquet files back to S3.
    """
    # List all files in the raw prefix
    processed_sorteos = list_processed_sorteos_in_partitioned_bucket(bucket_name)
    raw_files = list_files_in_s3(bucket_name, raw_prefix)
    
    print(f"Found {len(raw_files)} raw files in S3.")
    print(f"Found {len(processed_sorteos)} sorteos already processed")
    
    sorteos_df = pd.DataFrame()
    premios_df = pd.DataFrame()
    
    # Process each file
    for raw_file in raw_files:
        match = re.search(r"sorteo=(\d+)/", raw_file)
        if not match:
            print(f"Skipping file with unexpected structure: {raw_file}")
            continue

        numero_sorteo = int(match.group(1))
        if numero_sorteo in processed_sorteos:
            print(f"Skipping already processed sorteo {numero_sorteo}")
            continue

        local_path = f"/tmp/{os.path.basename(raw_file)}"
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
        premios_df = premios_df[["numero_sorteo", "numero_premiado", "letras", "monto", "vendedor", "ciudad", "departamento"]]

        premios_df.replace({"N/A": None, "n/a": None, "": None}, inplace=True)
        premios_df['numero_sorteo'] = pd.to_numeric(premios_df['numero_sorteo'], errors='coerce').fillna(0).astype(int)
        premios_df['numero_premiado'] = premios_df['numero_premiado'].astype(str)
        premios_df['letras'] = premios_df['letras'].astype(str)
        premios_df['monto'] = pd.to_numeric(premios_df['monto'], errors='coerce').fillna(0.0).astype(float)
        premios_df['vendedor'] = premios_df['vendedor'].astype(str)
        premios_df['ciudad'] = premios_df['ciudad'].astype(str)
        premios_df['departamento'] = premios_df['departamento'].astype(str)

        sorteos_df[['reintegro_primer_premio', 'reintegro_segundo_premio', 'reintegro_tercer_premio']] = sorteos_df['reintegros'].str.split(',', expand=True)
        sorteos_df.drop(columns=['reintegros'], inplace=True)

        numero_sorteo = sorteos_df['numero_sorteo'].iloc[0]
        fecha_sorteo = pd.to_datetime(sorteos_df["fecha_sorteo"].iloc[0], format='%d/%m/%Y', errors='coerce')
        year = fecha_sorteo.year if not pd.isna(fecha_sorteo) else "unknown"

        # Save and convert to .parquet files 
        partition_prefix = f"{processed_prefix}year={year}/sorteo={numero_sorteo}"
        sorteos_local_path = f"/tmp/sorteos_{numero_sorteo}.parquet"
        premios_local_path = f"/tmp/premios_{numero_sorteo}.parquet"

        sorteos_df.to_parquet(sorteos_local_path, index=False)
        premios_df.to_parquet(premios_local_path, index=False)

        simple_bucket = secrets["simple"]
        sorteos_key_simple = f"sorteos_{numero_sorteo}.parquet"
        premios_key_simple = f"premios_{numero_sorteo}.parquet"

        # Save files in simple bucket 
        sorteos_df.to_parquet(f"s3://{simple_bucket}/{processed_prefix}{sorteos_key_simple}", index=False)
        premios_df.to_parquet(f"s3://{simple_bucket}/{processed_prefix}{premios_key_simple}", index=False)

        partitioned_bucket = secrets["partitioned"]
        sorteos_df["year"] = year
        sorteos_df["sorteo"] = numero_sorteo
        premios_df["year"] = year
        premios_df["sorteo"] = numero_sorteo

        # Save files in partitioned bucket
        sorteos_df.to_parquet(f"s3://{partitioned_bucket}/processed/sorteos/", partition_cols=["year", "sorteo"])
        premios_df.to_parquet(f"s3://{partitioned_bucket}/processed/premios/", partition_cols=["year", "sorteo"])

        print(f"✅ Sorteo {numero_sorteo} procesado correctamente")


if __name__ == "__main__":
    secrets = get_secrets()
    raw_bucket = secrets["partitioned"]
    
    raw_prefix = "raw/"  # Carpeta donde están los archivos crudos
    processed_prefix = "processed/"  # Carpeta donde se subirán los archivos procesados
    print(f"Using raw bucket: {raw_bucket}")

    # Llama a la función orquestadora para realizar la transformación
    print("Starting dry test...")
    transform(raw_bucket, raw_prefix=raw_prefix, processed_prefix=processed_prefix)
    print("Dry test completed.")

