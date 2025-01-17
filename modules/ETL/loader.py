import pandas as pd
import pymysql
import json
import boto3
import os
import logging
from botocore.exceptions import ClientError
from tqdm import tqdm  # progress bar

# Configure logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper())

# Load configuration from AWS Secrets Manager
def get_config():
    secret_manager = boto3.client('secretsmanager', region_name=os.getenv("AWS_REGION"))
    config_secret_name = os.getenv("CONFIG_SECRET_NAME")
    
    try:
        secret_value = secret_manager.get_secret_value(SecretId=config_secret_name)
        secret = json.loads(secret_value['SecretString'])
        return secret
    except ClientError as e:
        logging.error(f"Failed to retreive secrets: {e}")
        raise

# Establish database connection
def get_db_credentials():
    config = get_config()
    secret_name = config.get("db_secret_name")
    region_name = config.get("aws_region")
    
    secret_manager = boto3.client('secretsmanager', region_name=region_name)
    
    try:
        secret_value = secret_manager.get_secret_value(SecretId=secret_name)
        secret = json.loads(secret_value['SecretString'])
        return secret
    except ClientError as e:
        logging.error(f"Failed to retrieve database credentials: {e}")
        raise 
    
# Establish database connection
def connect_to_db(credentials): # Pending to re-create DB and user name.
    try:
        connection = pymysql.connect(
            host=credentials['host'],
            user=credentials['username'],
            password=credentials['password'],
            database=credentials['db_name'],
            port=credentials.get('port', 3306),
            ssl={"ca": credentials.get('ssl_certificate')} if credentials.get('ssl_certificate') else None
        )
        logging.info("Successfully connected to the databaase")
        return connection
    except pymysql.MySQLError as e:
        logging.error(f"Database connection error: {e}")
        raise
    
# Close database connection
def close_db_connection(connection):
    if connection:
        connection.close()
        logging.info("Database connection closed.")    

# Load multiple CSVs into RDS
def load_csv_to_rds(connection, s3_bucket, csv_files, table_mapping, batch_size=1000):
    s3 = boto3.client('s3')
    try:
       for s3_key, table_name in table_mapping.items():
            local_path = f"/tmp/{os.path.basename(s3_key)}"
           
           # Donwload CSV file from S3
            with open(local_path, "wb") as f:
               s3.download_fileobj(s3_bucket, s3_key, f)
            logging.info(f"Downloaded {s3_key} from S3 bucket {s3_bucket}.")
            
            # Load CSV into DataFrame
            df = pd.read_csv(local_path)
            logging.info(f"Loaded CSV with {len(df)} rows from {s3_key}")
            
            # Prepare SQL DataFrame
            df = pd.read_csv(local_path)
            logging.info(f"Loaded CSV with {len(df)} rows from {s3_key}.")
            
            # Prepare SQL Statement
            columns = ", ".join(df.columns)
            placeholders = ", ".join(["%s"] * len(df.columns))
            update_clause = ", ".join([f"{col}=VALUES({col})" for col in df.columns])
            sql = f"""
                INSERT INTO {table_name} ({columns})
                VALUES ({placeholders})
                ON DUPLICATE KEY UPDATE {update_clause}
            """
            
            # Batch insert data into RDS
            data = [tuple(row) for row in df.to_numpy()]
            with connection.cursor() as cursor:
                for i in tqdm(range(0, len(data), batch_size), desc=f"Loading {table_name}"):
                    batch = data[i:i + batch_size]
                    cursor.executemany(sql, batch)
                connection.commit()
                logging.info(f"Successfully loaded data into {table_name}.")           
    except Exception as e:
        logging.error(f"Failed to load data into RDS: {e}")
        connection.rollback()
        raise

# Lambda handler
def lambda_handler(event, context):
    connection = None
    try:
        # Parse event data
        s3_bucket = event['s3_bucket']
        table_mappings = {
            "processed/sorteos.csv": "Sorteos",
            "processed/premios.csv": "Premios"
        }
        
        # Get database credentials and connect to RDS
        credentials = get_db_credentials()
        connection = connect_to_db(credentials)
        
        # Load CSVs to RDS 
        load_csv_to_rds(connection, s3_bucket, table_mappings.keys(), table_mappings)
        
    except Exception as e:
        logging.error(f"Lambda function failed: {e}")
        raise
    
    finally:
        close_db_connection(connection)