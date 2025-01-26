from sqlalchemy import create_engine
import pandas as pd
import boto3
import json
from botocore.exceptions import ClientError

# Get aws credentials
def get_secret():
    secret_name = "LotteryDBCredentials"
    region_name = "us-east-1"
    
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise e

    secret = json.loads(get_secret_value_response['SecretString'])
    return secret['username'], secret['password'], secret['host'], secret['db_name']

# download data as CSV
def export_table_to_csv(table_name, output_csv):
    username, password, host, db_name = get_secret()
    
    # Create an engine with SQLAchemy
    engine = create_engine(f"mysql+pymysql://{username}:{password}@{host}/{db_name}")
    try:
        query = f"SELECT * FROM {table_name}" # Select all data in the table
        df = pd.read_sql(query, engine) # Execute the query and save the dataframe
        df.to_csv(output_csv, index=False) # Exports to a csv file
        print(f"Data exported correctly to {output_csv}")
    except Exception as e:
        print(f"Error exporting data: {e}")
    finally:
        engine.dispose()
        
if __name__ == "__main__":
    export_table_to_csv("Sorteos", "./Data/downloaded/sorteos_export.csv")
    export_table_to_csv("Premios", "./Data/downloaded/premios_export.csv")
    export_table_to_csv("calendar_sorteos", "./Data/downloaded/calendar_export.csv")
    export_table_to_csv("letter_combinations", "./Data/downloaded/combinatios_export.csv")