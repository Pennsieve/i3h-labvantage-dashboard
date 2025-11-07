#!/usr/bin/env python3
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import sys

def convert_xlsx_to_parquet(xlsx_file, parquet_file):
    try:
        print(f"Reading XLSX file: {xlsx_file}")
        df = pd.read_excel(xlsx_file)

        print(f"XLSX file loaded. Shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")

        print(f"Converting date columns...")
        date_columns = ['VISITDATE']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        print(f"Writing to Parquet file: {parquet_file}")
        table = pa.Table.from_pandas(df)
        pq.write_table(table, parquet_file, compression='snappy')

        file_size_mb = pd.io.common.file_size(parquet_file) / (1024 * 1024)
        print(f"Conversion complete! Parquet file size: {file_size_mb:.2f} MB")

        print("\nFirst few rows of the data:")
        print(df.head())

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    xlsx_file = "data/LV export_101725.xlsx"
    parquet_file = "public/lv_export.parquet"

    convert_xlsx_to_parquet(xlsx_file, parquet_file)
