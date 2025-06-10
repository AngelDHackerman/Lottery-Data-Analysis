import os
import re
import boto3
from datetime import datetime

# Configuraciones
LOCAL_FOLDER = "../../../Data/raw/"  # cámbialo a tu path real
BUCKET_NAME = "lottery-raw-data-prod"
S3_PREFIX = "raw"  # base path dentro del bucket

# Cliente S3
s3 = boto3.client('s3')

# Regex para capturar número de sorteo y fecha del archivo si está incluida
sorteo_regex = re.compile(r"no\._?(\d+)", re.IGNORECASE)

# Recorremos los archivos .txt
for filename in os.listdir(LOCAL_FOLDER):
    if filename.endswith(".txt"):
        full_path = os.path.join(LOCAL_FOLDER, filename)

        # Intentar extraer el número de sorteo del nombre
        match = sorteo_regex.search(filename)
        if not match:
            print(f"No se pudo extraer el sorteo de {filename}")
            continue

        sorteo_number = match.group(1)

        # Leer archivo para extraer la fecha del sorteo
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        date_match = re.search(r"FECHA DEL SORTEO: (\d{2}/\d{2}/\d{4})", content)
        if not date_match:
            print(f"No se pudo encontrar la fecha en {filename}")
            continue

        fecha_sorteo = datetime.strptime(date_match.group(1), "%d/%m/%Y")
        year = fecha_sorteo.year

        # Construimos el path destino
        s3_key = f"{S3_PREFIX}/year={year}/sorteo={sorteo_number}/{filename}"

        # Subimos
        print(f"Subiendo {filename} a {s3_key}")
        s3.upload_file(full_path, BUCKET_NAME, s3_key)
