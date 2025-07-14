from urllib.parse import urlparse, parse_qs
from botocore.exceptions import ClientError
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import boto3
import json
import os
import re
import time

def upload_to_s3(local_file_path, s3_bucket, s3_key):
    s3 = boto3.client('s3')
    s3.upload_file(local_file_path, s3_bucket, s3_key)
    print(f"📤 File uploaded to S3: s3://{s3_bucket}/{s3_key}")
    

def check_if_sorteo_exists(s3_bucket, year, sorteo_number):
    s3 = boto3.client('s3')
    key = f"processed/year={year}/sorteo={sorteo_number}/sorteos.parquet"
    try: 
        s3.head_object(Bucket=s3_bucket, Key=key)
        print(f"🔁 Sorteo {sorteo_number} ya existe en {key}")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == "404":
            return False
        else:
            raise e