-- Convert CSV to Parquet using DuckDB
COPY (SELECT * FROM read_csv_auto('LV export_101725.csv')) 
TO 'public/lv_export.parquet' (FORMAT PARQUET);