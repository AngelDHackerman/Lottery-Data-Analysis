import pandas as pd

df = pd.read_parquet("./temp_files/sorteos.parquet")
print(df.head())
print(df.dtypes)
