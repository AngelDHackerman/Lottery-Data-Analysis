from pdfminer.high_level import extract_text

# Ruta al archivo PDF
pdf_path = "./images/gordito218.pdf"

# Extraer texto
text = extract_text(pdf_path)

# Ruta del archivo de texto de salida
output_txt_path = "output.txt"

# Extraer texto del PDF
text = extract_text(pdf_path)

# Guardar el texto en un archivo .txt
with open(output_txt_path, "w", encoding="utf-8") as txt_file:
    txt_file.write(text)

print(f"Texto extraído y guardado en {output_txt_path}")