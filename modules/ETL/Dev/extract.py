from urllib.parse import urlparse, parse_qs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import boto3
import json
import time
import logging
from modules.ETL.Dev.get_secrets_aws import get_secret

logging.basicConfig(level=logging.INFO)  

def upload_to_s3(content, s3_bucket, s3_key):
    """
    Uploads extracted content as a string to an S3 bucket.
    """
    s3 = boto3.client("s3")
    s3.put_object(Bucket=s3_bucket, Key=s3_key, Body=content.encode("utf-8"))
    logging.info(f"File uploaded to S3: s3://{s3_bucket}/{s3_key}")

def extract_lottery_data(lottery_number=None):
    """
    Extracts raw lottery data from the website and uploads it to S3.
    """
    # Get all secrets
    secrect_data = get_secret()
    s3_bucket = secrect_data["s3_bucket_raw"]