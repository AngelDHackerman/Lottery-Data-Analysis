# Note: the partitioned bucket is the "Source Of Truth" 
# there I validate if a lottery has or hasn't been processed.

import sys
import os
import re
import json
import pandas as pd
import boto3
from botocore.exceptions import ClientError
from awsglue.utils import getResolvedOptions 

from parser.parser import (
    split_header_body,
    process_header,
    process_body,
    split_vendido_por_column,
)

from extractor.s3_utils import (
    list_files_in_s3,
    list_processed_sorteos_in_partitioned_bucket,
    download_file_from_s3,
    upload_file_to_s3
)

from extractor.aws_secrets import get_secrets

buckets = get_secrets()
partitioned_bucket = buckets["partitioned"]
simple_bucket      = buckets["simple"]
    
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
    
    # Process each file and checks if already processed
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
            
        # Column cleaning in pandas
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

        sorteos_key_simple = f"sorteos_{numero_sorteo}.parquet"
        premios_key_simple = f"premios_{numero_sorteo}.parquet"

        # Save files in simple bucket 
        upload_file_to_s3(sorteos_local_path, simple_bucket, f"{processed_prefix}{sorteos_key_simple}")
        upload_file_to_s3(premios_local_path, simple_bucket, f"{processed_prefix}{premios_key_simple}")

        sorteos_df["year"] = year
        sorteos_df["sorteo"] = numero_sorteo
        premios_df["year"] = year
        premios_df["sorteo"] = numero_sorteo

        # Save files in partitioned bucket
        partitioned_sorteos_key = f"processed/sorteos/year={year}/sorteo={numero_sorteo}/sorteos.parquet"
        partitioned_premios_key = f"processed/premios/year={year}/sorteo={numero_sorteo}/premios.parquet"

        upload_file_to_s3(sorteos_local_path, partitioned_bucket, partitioned_sorteos_key)
        upload_file_to_s3(premios_local_path, partitioned_bucket, partitioned_premios_key)

        print(f"✅ Sorteo {numero_sorteo} procesado correctamente")
        
def main():
    """
    Entry point when running as a Glue Job.
    If the parameters are not provided, it will fall back to the Secrets Manager values.
    """
    args = getResolvedOptions(
        sys.argv,
        [
            'SIMPLE_BUCKET', 
            'PARTITIONED_BUCKET',
            'RAW_PREFIX', 
            'PROCESSED_PREFIX'
        ]
    )
    
    # Overwrites ONLY if they come in arguments (allows to continue testing locally)
    if args.get('PARTITIONED_BUCKET'):
        globals()['partitioned_bucket'] = args['PARTITIONED_BUCKET']
    if args.get('SIMPLE_BUCKET'):
        globals()['simple_bucket'] = args['SIMPLE_BUCKET']

    raw_prefix       = args['RAW_PREFIX']
    processed_prefix = args['PROCESSED_PREFIX']
    
    print(f"Starting Glue Job for bucket {partitioned_bucket}")
    transform(partitioned_bucket, raw_prefix, processed_prefix)
    print("Glue Job finished!")

if __name__ == "__main__":
    # raw_prefix = "raw/"  # Carpeta donde están los archivos crudos
    # processed_prefix = "processed/"  # Carpeta donde se subirán los archivos procesados
    # print(f"Using raw bucket: {partitioned_bucket}")
    # print("Starting dry test...")
    # transform(partitioned_bucket, raw_prefix=raw_prefix, processed_prefix=processed_prefix)
    # print("Dry test completed.")
    main()
