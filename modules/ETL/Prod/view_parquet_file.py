import pyarrow.parquet as pq

table = pq.read_table("./temp_files/premios.parquet")
print("Schema:")
print(table.schema)          # columnas y tipos
print("\nFilas totales:", table.num_rows)
