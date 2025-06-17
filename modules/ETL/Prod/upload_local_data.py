import os
import re
import boto3
import json
from datetime import datetime
from botocore.exceptions import ClientError

# Get secrets from AWS Secrets Manager
def get_bucket_names():
    secret_name = "lottery_secret_prod_2"
    region_name = "us-east-1"

    session = boto3.session.Session()
    client = session.client("secretsmanager", region_name=region_name)

    try:
        response = client.get_secret_value(SecretId=secret_name)
        secret = json.loads(response["SecretString"])
        return {
            "simple": secret["s3_bucket_simple_data_storage_prod_arn"].split(":::")[-1],
            "partitioned": secret["s3_bucket_partitioned_data_storage_prod_arn"].split(":::")[-1],
        }
    except ClientError as e:
        raise RuntimeError(f"Error fetching secrets: {e}")

# Upload file to S3 Bucket
def upload_to_s3(bucket_name, s3_key, local_path):
    s3 = boto3.client('s3')
    print(f"⬆️  Uploading to s3://{bucket_name}/{s3_key}")
    s3.upload_file(local_path, bucket_name, s3_key)
    
# Setup
LOCAL_FOLDER = "../../../Data/raw/" 
S3_PREFIX = "raw"
buckets = get_bucket_names() 

# Regex for sorteo y date
sorteo_regex = re.compile(r"sorteo(?:_[a-z]+)?_no\.?_?(\d+)", re.IGNORECASE)

# Process
for filename in os.listdir(LOCAL_FOLDER):
    if filename.endswith(".txt"):
        full_path = os.path.join(LOCAL_FOLDER, filename)

        match = sorteo_regex.search(filename)
        if not match:
            print(f"⚠️ No se pudo extraer el número de sorteo de {filename}")
            continue

        sorteo_number = match.group(1)

        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        date_match = re.search(r"FECHA DEL SORTEO: (\d{2}/\d{2}/\d{4})", content)
        if not date_match:
            print(f"⚠️ No se encontró la fecha del sorteo en {filename}")
            continue

        fecha_sorteo = datetime.strptime(date_match.group(1), "%d/%m/%Y")
        year = fecha_sorteo.year

        # 1️⃣ Guardar en bucket particionado (estructura Hive)
        key_hive = f"{S3_PREFIX}/year={year}/sorteo={sorteo_number}/{filename}"
        upload_to_s3(buckets["partitioned"], key_hive, full_path)

        # 2️⃣ Guardar en bucket simple
        key_simple = f"{S3_PREFIX}/sorteo_{sorteo_number}.txt"
        upload_to_s3(buckets["simple"], key_simple, full_path)