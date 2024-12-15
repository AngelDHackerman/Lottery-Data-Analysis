import os
from modules.ETL.extract import extract_lottery_data
from modules.ETL.transformer import transform
from modules.ETL.loader import get_secret, connect_to_db, load_csv_to_table, close_db_connection

def main():
    # Step 1: Extract
    # lottery_number = 208
    # output_path = extract_lottery_data(lottery_number)
    # print(f"Extracted file saved to: {output_path}")
    
    # Step 2: Transform the raw data
    input_folder = "./Data/raw/"
    output_folder = "./Data/processed"
    
    try:
        sorteos_csv, premios_csv = transform(input_folder, output_folder)
        print(f"Processing completed. CSVs generated:\n - Sorteos: {sorteos_csv}\n - Premios: {premios_csv}")
    except Exception as e:
        print(f"An error occurred: {e}")
        
    # Step 3: Load data to database
    

    
if __name__ == "__main__":
    main()