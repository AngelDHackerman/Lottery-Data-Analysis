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

    secret_name = "lottery_secret_prod"
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

def list_files_in_s3(bucket_name, prefix):
    """
    Lists all files in a specific S3 bucket folder.
    Args:
        bucket_name (str): Name of the S3 bucket.
        prefix (str): Prefix (folder path) to list files from.
    Returns:
        list: List of file keys.
    """
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    return [content['Key'] for content in response.get('Contents', [])]

def download_file_from_s3(bucke_name, s3_key, local_path):
    """
    Downloads a file from S3 to the local filesystem.
    """
    s3 = boto3.client('s3')
    s3.download_file(bucke_name, s3_key, local_path)
    print(f"Downloaded {s3_key} to {local_path}")
    
def upload_file_to_s3(local_path, bucket_name, s3_key):
    """
    Uploads a file from the local filesystem to S3.
    """
    s3 = boto3.client('s3')
    s3.upload_file(local_path, bucket_name, s3_key)
    print(f"Uploaded {local_path} to s3://{bucket_name}/{s3_key}")
    
def split_header_body(content_lines):
    """
    Splits the content of a file into HEADER and BODY sections.
    Args:
        content_lines (list): List of lines in the file.
    Returns:
        tuple: HEADER and BODY sections as lists of strings.
    """
    # Limpia las líneas antes de buscar
    content_cleaned = [line.strip() for line in content_lines if line.strip()]
    
    try:
        header_start = content_cleaned.index("HEADER")
        body_start = content_cleaned.index("BODY")
    except ValueError:
        print("Content does not contain 'HEADER' or 'BODY'. Debugging content:")
        # print(content_cleaned)  # Imprime el contenido para depuración
        raise ValueError("The file does not contain expected HEADER or BODY sections.")
    
    header = content_cleaned[header_start + 1 : body_start] # splits the information for header dataset
    body = content_cleaned[body_start + 1 :] # splits the information for body dataset
    
    return header, body


def process_header(header):
    """
    Processes the HEADER section and extracts relevant fields.
    Args:
        header (list): List of lines in the HEADER section.
    Returns:
        dict: Extracted data from the HEADER section.
    """
    # Regular expressions for extract specific information in header
    try:
        numero_sorteo = re.search(r"NO. (\d+)", header[0]).group(1)
        tipo_sorteo = re.search(r"SORTEO (\w+)", header[0], re.IGNORECASE).group(1)
        fecha_sorteo = re.search(r"FECHA DEL SORTEO: ([\d/]+)", " ".join(header)).group(1)
        fecha_caducidad = re.search(r"FECHA DE CADUCIDAD: ([\d/]+)", " ".join(header)).group(1)
        premios = re.search(r"PRIMER PREMIO (\d+) \|\|\| SEGUNDO PREMIO (\d+) \|\|\| TERCER PREMIO (\d+)", " ".join(header))
        primer_premio, segundo_premio, tercer_premio = premios.groups()
        reintegros = re.search(r"REINTEGROS ([\d, ]+)", " ".join(header)).group(1).replace(" ", "")
    except AttributeError as e:
        print("An error occurred while processing the HEADER.")
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
    Args:
        bucket_name (str): Name of the S3 bucket.
        raw_prefix (str): Prefix for raw data in S3 (e.g., "raw/").
        processed_prefix (str): Prefix for processed data in S3 (e.g., "processed/").
    """
    # List all files in the raw prefix
    raw_files = list_files_in_s3(bucket_name, raw_prefix)
    print(f"Found {len(raw_files)} raw files in S3.")
    
    sorteos_df = pd.DataFrame()
    premios_df = pd.DataFrame()
    
    # Process each file
    for raw_file in raw_files:
        local_path = f"/tmp/{os.path.basename(raw_file)}"
        
        # Download the file from S3 
        download_file_from_s3(bucket_name, raw_file, local_path)
        
        # Read the file content
        with open(local_path, "r", encoding="utf-8") as file:
            file_content = file.read()
            
        # Process the file
        header, body = split_header_body(file_content.splitlines())
        sorteos = [process_header(header)]
        premios = process_body(body)
        
        # Associate Sorteos with Premios
        for premio in premios:
            premio["numero_sorteo"] = sorteos[0]["numero_sorteo"]
        
        # Create individual DataFrames
        sorteos_df = pd.DataFrame(sorteos)
        premios_df = pd.DataFrame(premios)
    
        # Split 'vendido_por' into separate columns 
        premios_df = split_vendido_por_column(premios_df)
        # If city is "DE ESTA CAPITAL", then assign the "Departamento" as "Guatemala"
        premios_df.loc[premios_df['ciudad'].str.upper() == "DE ESTA CAPITAL", 'departamento'] = "GUATEMALA"
        # Reorder columns in premios_df
        premios_df = premios_df[
            [
                "numero_sorteo", "numero_premiado", "letras", "monto", "vendedor", "ciudad", "departamento"
            ]
        ]
        
        # Validate and clean data
        premios_df.replace({"N/A": None, "n/a": None, "": None}, inplace=True) # Reemplazar valores como "N/A" o similares por NaN
        premios_df['numero_sorteo'] = pd.to_numeric(premios_df['numero_sorteo'], errors='coerce').fillna(0).astype(int)
        premios_df['numero_premiado'] = premios_df['numero_premiado'].astype(str)
        premios_df['letras'] = premios_df['letras'].astype(str)
        premios_df['monto'] = pd.to_numeric(premios_df['monto'], errors='coerce').fillna(0.0).astype(float)
        premios_df['vendedor'] = premios_df['vendedor'].astype(str) # this keeps the value as None for compatibility
        premios_df['ciudad'] = premios_df['ciudad'].astype(str)
        premios_df['departamento'] = premios_df['departamento'].astype(str)    
        
        # Transform the sorteos' column "reintegros" into 3 different columns for better analysis
        sorteos_df[[
            'reintegro_primer_premio', 
            'reintegro_segundo_premio', 
            'reintegro_tercer_premio'
        ]] = sorteos_df['reintegros'].str.split(',', expand=True)

        # Remove the original 'reintegros' column
        sorteos_df.drop(columns=['reintegros'], inplace=True)

        # Determine the number and year of the draw
        numero_sorteo = sorteos_df['numero_sorteo'].iloc[0]
        fecha_sorteo = pd.to_datetime(sorteos_df["fecha_sorteo"].iloc[0], format='%d/%m/%Y', errors='coerce')
        year = fecha_sorteo.year if not pd.isna(fecha_sorteo) else "unknown"
        
        # Save transformed data to local Apache Parquet files and Partition Routes
        partition_prefix = f"{processed_prefix}year={year}/sorteo={numero_sorteo}"
        sorteos_local_path = f"/tmp/sorteos_{numero_sorteo}.parquet"
        premios_local_path = f"/tmp/premios_{numero_sorteo}.parquet"
        
        # Save to Parquet
        sorteos_df.to_parquet(sorteos_local_path, index=False)
        premios_df.to_parquet(premios_local_path, index=False)
        
        # Save simple version for EDA
        simple_bucket = secrets["simple"]
        
        sorteos_key_simple = f"sorteos_{numero_sorteo}.parquet"
        premios_key_simple = f"premios_{numero_sorteo}.parquet"
        
        sorteos_df.to_parquet(f"s3://{simple_bucket}/{processed_prefix}{sorteos_key_simple}", index=False)
        premios_df.to_parquet(f"s3://{simple_bucket}/{processed_prefix}{premios_key_simple}", index=False)

        # Save partitioned version for Glue/Athena
        partitioned_bucket = secrets["partitioned"]
        
        sorteos_df["year"] = year
        sorteos_df["sorteo"] = numero_sorteo
        premios_df["year"] = year
        premios_df["sorteo"] = numero_sorteo
        
        sorteos_df.to_parquet(f"s3://{partitioned_bucket}/processed/sorteos/", partition_cols=["year", "sorteo"])
        premios_df.to_parquet(f"s3://{partitioned_bucket}/processed/premios/", partition_cols=["year", "sorteo"])


        print("Transformation completed and files uploaded to S3.")


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

