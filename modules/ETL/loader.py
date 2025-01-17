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
    
def load_csv_to_table(connection, csv_file, table_name, batch_size=1000):
    """
    Load a CSV file into a specific database table using batched inserts.
    """
    # validate table name 
    if not re.match(r"^[a-zA-Z0-9_]+$", table_name):
        raise ValueError("Invalid table name. Only alphanumeric characters and underscores are allowed.")
    
    try:
        # Read CSV into DataFrame
        df = pd.read_csv(csv_file)
        logging.info(f"Loaded CSV {csv_file} with {len(df)} rows.")
        
        # Replace NaN with None for SQL compatibility
        df = df.where(pd.notnull(df), None)
        
        # Generate SQL and Convert DataFrame to list of tuples for efficient insertion
        columns = ", ".join(df.columns)
        placeholders = ", ".join(["%s"] * len(df.columns))
        # Adjust SQL query based on ignore_duplicate flag
        # Generar SQL dinámicamente con ON DUPLICATE KEY UPDATE
        update_columns = ", ".join([f"{col}=VALUES({col})" for col in df.columns])

        sql = f"""
            INSERT INTO {table_name} ({columns})
            VALUES ({placeholders})
            ON DUPLICATE KEY UPDATE {update_columns};
        """

        data = [tuple(row) for row in df.to_numpy()]
        
        # Batch insert with progress bar
        with connection.cursor() as cursor:
            for i in tqdm(range(0, len(data), batch_size), desc=f"Loading {table_name}"):
                batch = data[i:i + batch_size]
                cursor.executemany(sql, batch)  # Batch insert, optimizes performance when working with large volumes of data.
        connection.commit()
        logging.info(f"Data from {csv_file} loaded into table {table_name}.")
    except Exception as e:
        logging.error(f"Error loading CSV {csv_file} into table {table_name}: {e}")
        connection.rollback()
        raise

    
def close_db_connection(connection):
    """
    Close the database connection.
    
    Args:
        connection: The pymysql connection object.
        
    Returns:
        None
    """
    if connection:
        connection.close()
        logging.info("Database connection closed.")
        
def start_upload_multiple_csv_files(csv_files_and_tables):
    """
    Orchestrates the complete upload process of the CSV to the database.
    """
    connection = None # Initialize connection
    try:
        # Get database credentials
        username, password, host, db_name, ssl_cert_content = get_secret()
        
        # Connect to the database
        connection = connect_to_db(
            user=username, 
            password=password, 
            host=host, 
            database=db_name,
            ssl_cert_content=ssl_cert_content
        )
        
        # Upload each CSV file to its respective table
        for csv_file, table_name in csv_files_and_tables:
            logging.info(f"Starting upload for {csv_file} to table {table_name}")
            load_csv_to_table(connection, csv_file, table_name)
            
    except FileNotFoundError as e:
        logging.error(f"Certificate error: {e}")
        raise
    except Exception as e:
        logging.error(f"Error in upload process: {e}")
        raise
    finally:
        close_db_connection(connection)
