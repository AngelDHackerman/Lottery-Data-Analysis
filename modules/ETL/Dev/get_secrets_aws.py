
import boto3
import json
import logging

import boto3.session

def get_secret(secret_name="lottery_secret_dev", region_name="us-east-1"):
    """
    Retrieves the specified secret from AWS Secrets Manager.
    """
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)
    
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        secret = json.loads(get_secret_value_response["SecretString"])
        logging.info(f"Successfully retrieved secret: {secret_name}")
        return secret
    except Exception as e:
        logging.error(f"Error fetching secret {secret_name}: {e}")
        raise
    
# Gets all secrets of AWS Secrets Manager using a json format