import os
import pandas as pd
import re
import csv

def read_files(folder_path):
    # Reads all files starting with 'results_raw' from a folder.
    files = [f for f in os.listdir(folder_path) if f.startswith("results_raw")]
    dataframes = []
    # Add the file name and it's content to a dictionary "dataframes"
    for file in files:
        with open(os.path.join(folder_path, file), "r", encoding="utf-8") as f:
            lines = f.readlines()
            dataframes.append({"filename": file, "content": lines})
    return dataframes


def split_header_body(content):
    # Limpia las líneas antes de buscar
    content_cleaned = [line.strip() for line in content if line.strip()]
    
    try:
        header_start = content_cleaned.index("HEADER")
        body_start = content_cleaned.index("BODY")
    except ValueError:
        print("Content does not contain 'HEADER' or 'BODY'. Debugging content:")
        # print(content_cleaned)  # Imprime el contenido para depuración
        raise ValueError("The file does not contain expected HEADER or BODY sections.")
    
    header = content_cleaned[header_start + 1 : body_start]
    body = content_cleaned[body_start + 1 :]
    
    return header, body


def process_header(header):
    # print("Debugging header content:")
    # print(header)  # Verificar el contenido del header
    try:
        numero_sorteo = re.search(r"NO. (\d+)", header[0]).group(1)
        tipo_sorteo = re.search(r"SORTEO (\w+)", header[0], re.IGNORECASE).group(1)
        fecha_sorteo = re.search(r"FECHA DEL SORTEO: ([\d/]+)", " ".join(header)).group(1)
        fecha_caducidad = re.search(r"FECHA DE CADUCIDAD: ([\d/]+)", " ".join(header)).group(1)
        premios = re.search(r"PRIMER PREMIO (\d+) \|\|\| SEGUNDO PREMIO (\d+) \|\|\| TERCER PREMIO (\d+)", " ".join(header))
        primer_premio, segundo_premio, tercer_premio = premios.groups()
        reintegros = re.search(r"REINTEGROS ([\d, ]+)", " ".join(header)).group(1).replace(" ", "")
    except AttributeError as e:
        print("An error occurred while processing the HEADER.")
        raise ValueError("The HEADER does not contain the expected format.") from e
    
    return {
        "numero_sorteo": int(numero_sorteo),
        "tipo_sorteo": tipo_sorteo,
        "fecha_sorteo": fecha_sorteo,
        "fecha_caducidad": fecha_caducidad,
        "primer_premio": int(primer_premio),
        "segundo_premio": int(segundo_premio),
        "tercer_premio": int(tercer_premio),
        "reintegros": reintegros
    }



def process_body(body):
    # Processes the BODY and extracts relevant fields.
    premios_data = []
    last_premio_index = None  # Índice del último premio procesado

    for idx, line in enumerate(body):
        line = line.strip()
        if not line:  # Si la línea está vacía, ignórala
            continue

        # Intentar coincidir con una línea de premio
        match = re.match(r"(\d+)\s+(\w+)\s+\.+\s+([\d,]+\.?\d*)", line)
        if match:
            numero_premiado, letras, monto = match.groups()
            monto = float(monto.replace(",", ""))  # Limpia el monto
            premios_data.append({
                "numero_premiado": numero_premiado,
                "letras": letras,
                "monto": monto,
                "vendido_por": None,  # Por defecto, no tiene vendedor
            })
            last_premio_index = len(premios_data) - 1  # Guarda el índice actual

        elif "VENDIDO POR" in line and last_premio_index is not None:
            # Si encontramos "VENDIDO POR", asignar al último premio
            current_vendedor = line.split("VENDIDO POR", 1)[1].strip()
            premios_data[last_premio_index]["vendido_por"] = current_vendedor

    return premios_data


def split_vendido_por_column(df):
    """
    Splits the 'vendido_por' column into 'vendedor', 'ciudad', and 'departamento'.
    
    Args:
        df (pd.DataFrame): DataFrame with 'vendido_por' column.
        
    Returns:
        pd.DataFrame: DataFrame with new columns and 'vendido_por' removed.
    """
    split_data = df['vendido_por'].str.split(r',', expand=True)
    df['vendedor'] = split_data[0].str.strip()  # Extract vendor name
    df['ciudad'] = split_data[1].str.strip() if split_data.shape[1] > 1 else None  # Extract city
    df['departamento'] = split_data[2].str.strip() if split_data.shape[1] > 2 else None  # Extract department
    df.drop(columns=['vendido_por'], inplace=True)  # Remove original column
    return df


def validate_and_clean_data(df):
    """
    Validates and cleans data types in a DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame to validate and clean.
        
    Returns:
        pd.DataFrame: Cleaned DataFrame with correct types.
    """
    # Reemplazar valores como "N/A" o similares por NaN
    df.replace({"N/A": None, "n/a": None, "": None}, inplace=True)
    
    # Validate and convert types, also replace null values with "N/A"
    df['numero_sorteo'] = pd.to_numeric(df['numero_sorteo'], errors='coerce').fillna(0).astype(int)
    df['numero_premiado'] = df['numero_premiado'].astype(str)
    df['letras'] = df['letras'].astype(str)
    df['monto'] = pd.to_numeric(df['monto'], errors='coerce').fillna(0.0).astype(float)
    df['vendedor'] = df['vendedor'].fillna("N/A").astype(str)
    df['ciudad'] = df['ciudad'].fillna("N/A").astype(str)
    df['departamento'] = df['departamento'].fillna("N/A").astype(str)

    return df


def transform(folder_path, output_folder="./processed"):
    # Orchestrates the complete transformation process and exports to CSV.
    # Read and process files
    dataframes = read_files(folder_path)
    sorteos = []
    premios = []

    for df in dataframes:
        header, body = split_header_body(df["content"])

        # Process HEADER
        sorteos.append(process_header(header))

        # Process BODY
        body_data = process_body(body)
        for premio in body_data:
            premio["numero_sorteo"] = sorteos[-1]["numero_sorteo"]  # Map with the draw number
            premios.append(premio)

    # Convert results to DataFrames
    sorteos_df = pd.DataFrame(sorteos)
    premios_df = pd.DataFrame(premios)
    
    # Transform the column 'reintegros' into 3 different columns for better analysis
    sorteos_df[[
        'reintegro_primer_premio', 
        'reintegro_segundo_premio', 
        'reintegro_tercer_premio'
        ]] = sorteos_df['reintegros'].str.split(',', expand=True)
    
    # Remove the original 'reintegros' column
    sorteos_df.drop(columns=['reintegros'], inplace=True)
    
    # reorder columns for "premios" (body dataframe)
    columns_order = ["numero_sorteo", "numero_premiado", "letras", "monto", "vendido_por"]
    premios_df = pd.DataFrame(premios, columns=columns_order)
    
    # Validate sorteos DataFrame
    if sorteos_df.isnull().values.any():
        print("Null values detected in sorteos.csv. Removing invalid rows")
        sorteos_df.dropna(inplace=True) # Remove rows with null values
        
    # Validate premios DataFrame
    if premios_df.isnull().values.any():
        print("Null values detected in premios.csv. Filling missing data.")
        premios_df['vendido_por'] = premios_df['vendido_por'].fillna("N/A")  # Replace nulls with default value
        premios_df.dropna(inplace=True) # Remove rows with null values
        
    # Split "Vendido_por" column into vendedor, ciudad and departamento
    premios_df = split_vendido_por_column(premios_df)

    # If city is "DE ESTA CAPITAL", then assign the "Departamento" as "Guatemala"
    premios_df.loc[premios_df['ciudad'].str.upper() == "DE ESTA CAPITAL", 'departamento'] = "GUATEMALA"
    
    # Validate and clean data types
    premios_df = validate_and_clean_data(premios_df)
    
    # validate dates in sorteo.csv
    sorteos_df['fecha_sorteo'] = pd.to_datetime(sorteos_df['fecha_sorteo'], format='%d/%m/%Y', errors='coerce')
    sorteos_df['fecha_caducidad'] = pd.to_datetime(sorteos_df['fecha_caducidad'], format='%d/%m/%Y', errors='coerce')
    
    # Validate output columns 
    required_columns_sorteos = ["numero_sorteo", "tipo_sorteo", "fecha_sorteo", "fecha_caducidad", 
                                "primer_premio", "segundo_premio", "tercer_premio", 
                                "reintegro_primer_premio", "reintegro_segundo_premio", "reintegro_tercer_premio"]
    required_columns_premios = ["numero_sorteo", "numero_premiado", "letras", "monto", "vendedor", "ciudad", "departamento"]
    
    if not all (col in sorteos_df.columns for col in required_columns_sorteos):
        raise ValueError("sorteos.csv does not contain all required columns.")
    if not all (col in premios_df.columns for col in required_columns_premios):
        raise ValueError("premios.csv does not contain all required columns.")

    # Validate the output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    # Export DataFrames to CSV
    sorteos_csv = os.path.join(output_folder, "sorteos.csv")
    premios_csv = os.path.join(output_folder, "premios.csv")
    
    sorteos_df.to_csv(sorteos_csv, index=False, quoting=csv.QUOTE_NONE, escapechar='\\')
    premios_df.to_csv(premios_csv, index=False, quoting=csv.QUOTE_NONE, escapechar='\\')
    
    # These lines validate that the generated CSV files are readable and correctly formatted.
    pd.read_csv(sorteos_csv, escapechar='\\')  # Ensures sorteos.csv is well-formatted
    pd.read_csv(premios_csv, escapechar='\\')  # Ensures premios.csv is well-formatted

    print(f"Exported sorteos to {sorteos_csv}")
    print(f"Exported premios to {premios_csv}")
    # print(header)
    

    return sorteos_csv, premios_csv
