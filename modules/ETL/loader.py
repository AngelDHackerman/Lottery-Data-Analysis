import pandas as pd
import pymysql
import boto3
from botocore.exceptions import ClientError
import os
import logging
import json
import re
from tqdm import tqdm # progress bar
import tempfile

# Configure logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper())

# Get the secret from AWS Secrets Manager
def get_secret():

    secret_name = "LotteryDBCredentials"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    # Parse the secret string into a dictionary
    secret = json.loads(get_secret_value_response['SecretString'])
    return secret['username'], secret['password'], secret['host'], secret['db_name'], secret['ssl_certificate']

def connect_to_db(user, password, host, database, port=3306, ssl_cert_content=None):
    """
    Establish a connection to the database with optional SSL.
    """
    try:   
        ssl_params = None
        
        if ssl_cert_content: 
            # Create a temporal file for the SSL Certificate
            with tempfile.NamedTemporaryFile(delete=False, mode='w') as temp_cert:
                temp_cert.write(ssl_cert_content)
                temp_cert_path= temp_cert.name
                ssl_params = {'ssl': {'ca': temp_cert_path}}
                
        # Stablish connection
        connection = pymysql.connect(
            user=user,
            password=password,
            host=host,
            database=database,
            port=port,
            ssl=ssl_params
        )
        logging.info("Database connection established.")
        
        # Check SSL status
        with connection.cursor() as cursor:
            cursor.execute("SHOW STATUS LIKE 'Ssl_cipher';")
            ssl_status = cursor.fetchone()
            logging.info(f"SSL Cipher: {ssl_status[1] if ssl_status else 'None'}")
        
        return connection
    except pymysql.MySQLError as e:
        logging.error(f"Error connecting to database: {e}")
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
