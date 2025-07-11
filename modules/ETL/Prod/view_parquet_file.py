import pyarrow.parquet as pq

table = pq.read_table("test_sorteo_3046.parquet")
print("Schema:")
print(table.schema)          # columnas y tipos
print("\nFilas totales:", table.num_rows)
