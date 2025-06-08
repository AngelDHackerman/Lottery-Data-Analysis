from urllib.parse import urlparse, parse_qs
from botocore.exceptions import ClientError
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import boto3
import json
import os
import time

# Get the secret from AWS Secrets Manager
def get_secret():

    secret_name = "lottery_secret_dev"
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
    return secret['s3_bucket_raw']

def upload_to_s3(local_file_path, s3_bucket, s3_key):
    """
    Uploads a file to an S3 bucket.
    """
    s3 = boto3.client('s3')
    s3.upload_file(local_file_path, s3_bucket, s3_key)
    print(f"File uploaded to S3: s3://{s3_bucket}/{s3_key}")

def extract_lottery_data(lottery_number=None, output_folder="/tmp", s3_bucket=None):
    """
    Extracts raw lottery data for a given lottery number or the latest lottery.
    Saves the data to a .txt file and optionally uploads it to S3.

    Args:
        lottery_number (int, optional): The ID of the lottery to extract. If None, extracts the latest lottery.
        output_folder (str): Folder where the extracted data will be temporarily saved.
        s3_bucket (str, optional): S3 bucket to upload the extracted file.

    Returns:
        str: Path to the saved .txt file.
    """
    # Configure WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    
    try:
        # Open the target URL
        url = 'https://loteria.org.gt/site/award'
        driver.get(url)
        wait = WebDriverWait(driver, 10)

        # Close pop-up ad if present
        try: 
            close_ad = wait.until(EC.visibility_of_element_located((By.ID, "ocultarAnuncio")))
            # Click on the "close button" using javascript
            driver.execute_script("arguments[0].click();", close_ad)
        except Exception:
            print("No pop-up ad found.")
            
        # Determine the lottery number to extract
        if lottery_number:
            print(f"Extracting data for lottery ID: {lottery_number}")
            lottery_xpath = f"//a[contains(@href, 'id={lottery_number}') and contains(text(), 'Sorteo')]"
            selected_lottery_id = lottery_number # Use the manually provided ID
        else:
            print("Extracting data for the latest lottery.")
            lottery_xpath = "//body/div[3]/div[1]/div/div[2]/div[1]/div/div/div/a"

        # Click on the lottery number link
        element = wait.until(EC.presence_of_element_located((By.XPATH, lottery_xpath)))
        driver.execute_script("arguments[0].click();", element)
        
        # Extract the current URL 
        current_url = driver.current_url
        print(f"Current URL: {current_url}")
        
        # Extract the ID from the URL if no lottery_number was provided
        if not lottery_number:
            parsed_url = urlparse(current_url)
            query_params = parse_qs(parsed_url.query)
            selected_lottery_id = query_params.get("id", [None])[0] # Get the 'id' parameter
            
            if not selected_lottery_id:
                raise ValueError("Failed to extract lottery ID from the URL")
            
        print(f"Selected Lottery ID: {selected_lottery_id}")

        # Extract HEADER information
        header = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "heading_s1.text-center")))
        header_text = header.text.strip()
        header_text = "\n".join(filter(lambda line: line.strip() != "", header_text.splitlines()))

        # Extract filename from HEADER
        header_sorteo_number = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h2"))).text.strip()
        header_sorteo_number = header_sorteo_number.lower()
        header_filename = header_sorteo_number.replace(" ", "_")

        # Extract BODY information
        body_content = wait.until(EC.presence_of_element_located(
            (By.XPATH, "(//div[@class='card-body']//div[@class='row'])[3]")  # Third 'row' inside 'card-body'
        ))
        body_results = body_content.text

        # Ensure the output folder exists
        os.makedirs(output_folder, exist_ok=True)

        # Save data to a .txt file
        file_name = f"results_raw_lottery_url_id_{selected_lottery_id}_{header_filename}.txt"
        output_path = os.path.join(output_folder, file_name)
        with open(output_path, "w", encoding="utf-8") as file:
            file.write("HEADER\n")
            file.write(header_text + "\n\n")
            file.write("BODY\n")
            if not body_results.startswith("00MIL"):
                file.write("CENTENARES\n")  # Add title to the first group
            file.write(body_results)

        print(f"Data extracted and saved to: {output_path}")
        
        # Upload to S3 Bucket
        if s3_bucket:
            s3_key = f"raw/{file_name}"
            upload_to_s3(output_path, s3_bucket, s3_key)
            
        return output_path
    
    finally:
        # Always close the browser
        driver.quit()

# Example usage

bucket_name = get_secret()
if not bucket_name:
    raise ValueError("The bucket name could not be retrieved from Secrets Manager.")

if __name__ == "__main__":
    extract_lottery_data(lottery_number=None, s3_bucket=bucket_name)