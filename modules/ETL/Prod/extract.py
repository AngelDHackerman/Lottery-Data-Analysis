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









# 🔧 Example usage
buckets = get_secrets()
partitioned_bucket = buckets["partitioned"]
simple_bucket = buckets["simple"]

if not partitioned_bucket:
    raise ValueError("The bucket name could not be retrieved from Secrets Manager.")

if __name__ == "__main__":
    extract_lottery_data(lottery_number=231)
