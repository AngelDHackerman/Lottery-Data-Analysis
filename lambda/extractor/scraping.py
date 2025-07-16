import os
import re
import requests
import logging
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup

from secrets import get_secrets
from s3_utils import upload_to_s3, check_if_sorteo_exists

logging.basicConfig(level=logging.INFO)

buckets = get_secrets()
partitioned_bucket = buckets["partitioned"]
simple_bucket      = buckets["simple"]

def extract_lottery_data(lottery_number=None, output_folder="/tmp"):
    base_url = "https://loteria.org.gt/site/award"
    session = requests.Session()
    
    # 1. Get the initial HTML
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    response = session.get(base_url, timeout= 25)
    soup = BeautifulSoup(response.content, "html.parser")
    
    # 2. Get the link of the "sorteo" (lastest one, or one in specific)
    if lottery_number:
        logging.info(f"🎯 Extracting data for lottery ID: {lottery_number}")
        sorteo_link = soup.find("a", href=lambda href: href and f"id={lottery_number}" in href)
    else:
        logging.info("🎯 Extracting data for the latest lottery.")
        sorteo_link = soup.select_one("div.container a[href*='id=']")  # first sorteo available, this is the best locator I could find
        
    if not sorteo_link:
        raise ValueError("❌ No se pudo encontrar el enlace al sorteo.")
    
    sorteo_url = sorteo_link["href"]
    selected_lottery_id = parse_qs(urlparse(sorteo_url).query).get("id", [None])[0]
    if not selected_lottery_id:
        raise ValueError("❌ No se pudo extraer el ID del sorteo desde la URL.")
    
    # 3. Visit the page of the specific "sorteo"
    response = session.get(sorteo_url if "http" in sorteo_url else f"https://loteria.org.gt{sorteo_url}")
    soup = BeautifulSoup(response.content, "html.parser")
    
    # 4. Extrae el encabezado 
    header_div = soup.select_one("div.heading_s1.text-center")
    header_text = header_div.get_text(separator="\n").strip() if header_div else ""
    header_title = soup.find("h2").text.strip()

    # Extraer el número real del sorteo desde el encabezado ------------------------------------------------------------------
    match_sorteo = re.search(r"SORTEO.*?NO\.?\s+(\d+)", header_title, re.IGNORECASE)
    if not match_sorteo:
        raise ValueError("❌ No se pudo extraer el número del sorteo.")
    numero_sorteo_real = int(match_sorteo.group(1))
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

    # 5. Extraer el BODY (resultados)
    # Basado en estructura observada: el tercer div.row dentro de .card-body
    result_divs = soup.select("div.card-body div.row")
    if len(result_divs) < 3:
        raise ValueError("❌ No se pudo encontrar la sección de resultados.")
    
    body_results = (
    result_divs[2].get_text(separator="\n")    # ① pon un separador
    .replace("\r", "")                         # ② limpia \r si hubiera
    )

    # 6. Guarda el archivo .txt localmente
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

    # 7. Dual upload to S3 
    # Hive-style path
    s3_key_hive = f"raw/year={year}/sorteo={numero_sorteo_real}/{file_name}"
    upload_to_s3(output_path, partitioned_bucket, s3_key_hive)

    # Simple path
    s3_key_simple = f"raw/sorteo_{numero_sorteo_real}.txt"
    upload_to_s3(output_path, simple_bucket, s3_key_simple)

    logging.info(f"✅ Sorteo {numero_sorteo_real} subido a ambos buckets.")
    return output_path
