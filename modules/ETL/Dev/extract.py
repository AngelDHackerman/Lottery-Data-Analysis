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
    
    # Configure Selenium WebDriver for AWS lambda
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sadbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    
    try:
        url = "https://loteria.org.gt/site/award"
        driver.get(url)
        wait =WebDriverWait(driver, 10)
        
        # Close ad
        try:
            close_ad = wait.until(EC.visibility_of_element_located((By.ID, "ocultarAnuncio")))
            driver.execute_script("arguments[0].click();", close_ad)
        except Exception:
            logging.info("No pop-up ad found!")
            
        # Determine which lottery extract
        if lottery_number:
            logging.info(f"Extracting data for lottery ID: {lottery_number}")
            lottery_xpath = f"//a[contains(@href, 'id={lottery_number}') and contains(text(), 'Sorteo')]"
            selected_lottery_id = lottery_number
        else:
            logging.info("Extracting latest lottery")
            lottery_xpath = "//body/div[3]/div[1]/div/div[2]/div[1]/div/div/div/a"
            
        # Click on the lottery number link
        element = wait.until(EC.presence_of_element_located((By.XPATH, lottery_xpath)))
        driver.execute_script("arguments[0].click();", element)
        
        # Extract the current URL
        current_url = driver.current_url
        
        # Extract the ID from the URL if no lottery_number was provided
        if not lottery_number:
            parsed_url = urlparse(current_url)
            query_params = parse_qs(parsed_url.query)
            selected_lottery_id =  query_params.get("id", [None])[0] # Get the 'id' parameter
            
            if not selected_lottery_id:
                raise ValueError("Failed to extract lottery ID from the URL")
        
        # Extract Header information
        header = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "heading_s1.text-center")))
        header_text = header.text.strip()
        header_text = "\n".join(filter(lambda line: line.strip() != "", header_text.splitlines())) # cleans header, removes empty lines
        
        # Extract filename from Header
        header_sorteo_number = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h2"))).text.strip()
        header_sorteo_number = header_sorteo_number.lower()
        header_filename = header_sorteo_number.replace(" ", "_")
        
        # Generate filename with detailed name
        file_name = f"resultds_raw_lottery_url_id_{selected_lottery_id}_{header_filename}.txt"
        s3_key = f"raw/{file_name}"
        
        # Extract Body information
        body_content = wait.until(EC.presence_of_element_located(
            (By.XPATH, "(//div[@class='card-body']//div[@class='row'])[3]") # Third 'row' inside 'card-body'
        )).text
        
        # Check if content needs tag "CENTENARES"
        if not body_content.startswith("00MIL"):
            body_content = "CENTENARES\n" + body_content
            
        # Format content with header and body splited
        file_content = f"HEADER\n{header_text}\nBODY\n{body_content}"
        
        # Upload file to S3 bucket
        upload_to_s3(file_content, s3_bucket, s3_key)
        
        logging.info(f"Extracted data successfully uploaded to {s3_key}")
        return {"s3_key": s3_key, "s3_bucket": s3_bucket}
    
    finally:
        driver.quit()
        
def lambda_handler(event, context):     # May be need to change to Docker Container instead of handler or lambda layers
    """
    AWS Lambda entry point for Step Functions
    """
    lottery_number = event.get("lottery_number")
    result = extract_lottery_data(lottery_number)
    return result
        
        