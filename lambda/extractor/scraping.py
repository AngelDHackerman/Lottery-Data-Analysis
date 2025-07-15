from urllib.parse import urlparse, parse_qs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import re
import logging

logging.basicConfig(level=logging.INFO)

from extractor.secrets import get_secrets
from extractor.s3_utils import upload_to_s3, check_if_sorteo_exists

buckets = get_secrets()
partitioned_bucket = buckets["partitioned"]
simple_bucket      = buckets["simple"]

def extract_lottery_data(lottery_number=None, output_folder="/tmp", s3_bucket=None):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    
    try:
        url = 'https://loteria.org.gt/site/award'
        driver.get(url)
        wait = WebDriverWait(driver, 30)

        try: 
            close_ad = wait.until(EC.visibility_of_element_located((By.ID, "ocultarAnuncio")))
            driver.execute_script("arguments[0].click();", close_ad)
        except Exception:
            logging.info("No pop-up ad found.")

        if lottery_number:
            logging.info(f"🎯 Extracting data for lottery ID: {lottery_number}")
            lottery_xpath = f"//a[contains(@href, 'id={lottery_number}') and contains(text(), 'Sorteo')]"
            selected_lottery_id = lottery_number
        else:
            logging.info("🎯 Extracting data for the latest lottery.")
            lottery_xpath = "//body/div[3]/div[1]/div/div[2]/div[1]/div/div/div/a"

        element = wait.until(EC.presence_of_element_located((By.XPATH, lottery_xpath)))
        driver.execute_script("arguments[0].click();", element)

        current_url = driver.current_url
        logging.info(f"🔗 Current URL: {current_url}")

        if not lottery_number:
            parsed_url = urlparse(current_url)
            query_params = parse_qs(parsed_url.query)
            selected_lottery_id = query_params.get("id", [None])[0]
            if not selected_lottery_id:
                raise ValueError("❌ Failed to extract lottery ID from the URL")
        
        logging.info(f"📌 Selected Lottery ID (URL): {selected_lottery_id}")
        
        # Extrae el encabezado 
        header = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "heading_s1.text-center")))
        header_text = header.text.strip()
        header_text = "\n".join(filter(lambda line: line.strip() != "", header_text.splitlines()))
        header_title = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h2"))).text.strip()

        # Extraer el número real del sorteo desde el encabezado
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
        if check_if_sorteo_exists(partitioned_bucket, year, numero_sorteo_real):
            logging.warning(f"⚠️ Sorteo {numero_sorteo_real} has already been processed. Canceling extraction.")
            return None

        # Extrae resultados del Body
        body_content = wait.until(EC.presence_of_element_located(
            (By.XPATH, "(//div[@class='card-body']//div[@class='row'])[3]")
        ))
        body_results = body_content.text

        # Guarda el archivo .txt localmente
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

        logging.info(f"💾 Data extracted and saved to: {output_path}")

        # Dual upload to S3 
        # Hive-style path
        s3_key_hive = f"raw/year={year}/sorteo={numero_sorteo_real}/{file_name}"
        upload_to_s3(output_path, partitioned_bucket, s3_key_hive)

        # Simple path
        s3_key_simple = f"raw/sorteo_{numero_sorteo_real}.txt"
        upload_to_s3(output_path, simple_bucket, s3_key_simple)

        logging.info(f"✅ Sorteo {numero_sorteo_real} subido a ambos buckets.")
        return output_path

    finally:
        driver.quit()