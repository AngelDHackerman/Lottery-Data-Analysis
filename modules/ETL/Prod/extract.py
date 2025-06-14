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

# Get the secret from AWS Secrets Manager
def get_secret():
    secret_name = "lottery_secret_dev"
    region_name = "us-east-1"
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise e
    secret = json.loads(get_secret_value_response['SecretString'])
    return secret['s3_bucket_raw']

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

def extract_lottery_data(lottery_number=None, output_folder="/tmp", s3_bucket=None):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    
    try:
        url = 'https://loteria.org.gt/site/award'
        driver.get(url)
        wait = WebDriverWait(driver, 10)

        try: 
            close_ad = wait.until(EC.visibility_of_element_located((By.ID, "ocultarAnuncio")))
            driver.execute_script("arguments[0].click();", close_ad)
        except Exception:
            print("No pop-up ad found.")

        if lottery_number:
            print(f"🎯 Extracting data for lottery ID: {lottery_number}")
            lottery_xpath = f"//a[contains(@href, 'id={lottery_number}') and contains(text(), 'Sorteo')]"
            selected_lottery_id = lottery_number
        else:
            print("🎯 Extracting data for the latest lottery.")
            lottery_xpath = "//body/div[3]/div[1]/div/div[2]/div[1]/div/div/div/a"

        element = wait.until(EC.presence_of_element_located((By.XPATH, lottery_xpath)))
        driver.execute_script("arguments[0].click();", element)

        current_url = driver.current_url
        print(f"🔗 Current URL: {current_url}")

        if not lottery_number:
            parsed_url = urlparse(current_url)
            query_params = parse_qs(parsed_url.query)
            selected_lottery_id = query_params.get("id", [None])[0]
            if not selected_lottery_id:
                raise ValueError("❌ Failed to extract lottery ID from the URL")
        
        print(f"📌 Selected Lottery ID (URL): {selected_lottery_id}")
        
        header = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "heading_s1.text-center")))
        header_text = header.text.strip()
        header_text = "\n".join(filter(lambda line: line.strip() != "", header_text.splitlines()))

        # Extraer el número real del sorteo desde el encabezado
        header_title = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h2"))).text.strip()
        match_sorteo = re.search(r"SORTEO.*?NO\.?\s+(\d+)", header_title, re.IGNORECASE)
        if match_sorteo:
            numero_sorteo_real = int(match_sorteo.group(1))
        else:
            raise ValueError("❌ The actual draw number could not be extracted from the header.")
        
        header_filename = header_title.lower().replace(" ", "_")

        # Extraer fecha del sorteo
        fecha_match = re.search(r"FECHA DEL SORTEO:\s*([\d/]+)", header_text)
        if fecha_match:
            fecha_sorteo_text = fecha_match.group(1)
            try:
                year = int(fecha_sorteo_text.split("/")[-1])
            except:
                year = "unknown"
        else:
            year = "unknown"
        
        # Verificar si ya fue procesado
        if check_if_sorteo_exists(s3_bucket, year, numero_sorteo_real):
            print(f"⚠️ Sorteo {numero_sorteo_real} has already been processed. Canceling extraction.")
            return None

        # BODY
        body_content = wait.until(EC.presence_of_element_located(
            (By.XPATH, "(//div[@class='card-body']//div[@class='row'])[3]")
        ))
        body_results = body_content.text

        os.makedirs(output_folder, exist_ok=True)
        file_name = f"results_raw_lottery_url_id_{selected_lottery_id}_{header_filename}.txt"
        output_path = os.path.join(output_folder, file_name)

        with open(output_path, "w", encoding="utf-8") as file:
            file.write("HEADER\n")
            file.write(header_text + "\n\n")
            file.write("BODY\n")
            if not body_results.startswith("00MIL"):
                file.write("CENTENARES\n")
            file.write(body_results)

        print(f"💾 Data extracted and saved to: {output_path}")

        if s3_bucket:
            s3_key = f"raw/year={year}/sorteo={numero_sorteo_real}/{file_name}"
            upload_to_s3(output_path, s3_bucket, s3_key)
            print(f"✅ Sorteo {numero_sorteo_real} saved as {file_name} and uploaded to {s3_key}")
        
        return output_path

    finally:
        driver.quit()

# 🔧 Example usage
bucket_name = get_secret()
if not bucket_name:
    raise ValueError("The bucket name could not be retrieved from Secrets Manager.")

if __name__ == "__main__":
    extract_lottery_data(lottery_number=228, s3_bucket=bucket_name)



 