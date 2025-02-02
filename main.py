import os
from modules.ETL.extract import extract_lottery_data
from modules.ETL.transformer import transform
from modules.ETL.loader import start_upload_multiple_csv_files

def main():
    # Step 1: Extract
    # Uncomment if extraction is needed
    lottery_number = 211
    
    output_path = extract_lottery_data(lottery_number)
    print(f"Extracted file saved to: {output_path}")
    
    # Step 2: Transform the raw data
    input_folder = "./Data/raw/"
    output_folder = "./Data/processed"
    
    try:
        sorteos_csv, premios_csv = transform(input_folder, output_folder)
        print(f"Processing completed. CSVs generated:\n - Sorteos: {sorteos_csv}\n - Premios: {premios_csv}")
    except Exception as e:
        print(f"An error occurred during transformation: {e}")
        return  # Exit on error#
    
    # Step 3: Load data to database
    csv_files_and_tables = [
        (sorteos_csv, "Sorteos"),
        (premios_csv, "Premios")
    ]
    try:
        start_upload_multiple_csv_files(csv_files_and_tables)
        print(f"All CSV files successfully uploaded to the database")
    except Exception as e:
        print(f"An error occurred during upload: {e}")
        
# Upload the calendar and letter combinations
# def upload_calendar_combinations_csv_files():
#     csv_files_and_tables = [
#         ("./Data/processed/calendar_sorteos.csv", "calendar_sorteos"),
#         ("./Data/processed/letter_combinations.csv", "letter_combinations")
#     ]
    
#     try:
#         start_upload_multiple_csv_files(csv_files_and_tables)
#         print("New CSV files successfully uploaded to the database.")
#     except Exception as e:
#         print(f"An error occurred while uploading new CSV files: {e}")

if __name__ == "__main__":
    main()
    # upload_calendar_combinations_csv_files()