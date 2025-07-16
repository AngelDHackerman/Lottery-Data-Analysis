from scraping import extract_lottery_data

if __name__ == "__main__":
    path = extract_lottery_data(lottery_number=236)  # Puedes usar None para el más reciente
    print(f"\n✅ TEST COMPLETADO. Archivo guardado: {path}")
