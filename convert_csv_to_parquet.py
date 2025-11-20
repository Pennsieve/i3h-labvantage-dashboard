#!/usr/bin/env python3
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import sys
import json
from pathlib import Path

def load_config(config_path):
    """Load the model configuration from JSON file"""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}", file=sys.stderr)
        sys.exit(1)
def apply_column_mapping(df, config):
    """Rename columns based on mapping in config"""
    column_mapping = config.get('column_mapping', {})
    
    if column_mapping:
        print(f"\nApplying column name mappings:")
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                print(f"  Renaming '{old_name}' -> '{new_name}'")
                df = df.rename(columns={old_name: new_name})
            else:
                print(f"  Warning: Column '{old_name}' not found in data")
    
    return df
def join_csvs(csv_files, data_dir, join_config):
    """Join multiple CSV files on the first common column"""
    print(f"Reading first CSV: {csv_files[0]}")
    df = pd.read_csv(Path(data_dir) / csv_files[0], low_memory=False)
    print(f"First CSV loaded. Shape: {df.shape}")
    
    if len(csv_files) > 1:
        # Get join type from config (default to 'left' to preserve all rows)
        join_type = join_config.get('type', 'left')
        join_column = join_config.get('column', None)
        
        for csv_file in csv_files[1:]:
            print(f"\nReading CSV: {csv_file}")
            df_next = pd.read_csv(Path(data_dir) / csv_file, low_memory=False)
            print(f"CSV loaded. Shape: {df_next.shape}")
            
            # Use specified join column or find first common column
            if join_column and join_column in df.columns and join_column in df_next.columns:
                join_col = join_column
            else:
                common_cols = [col for col in df.columns if col in df_next.columns]
                if not common_cols:
                    raise ValueError(f"No common columns found between files")
                join_col = common_cols[0]
            
            print(f"Joining on column: {join_col} (type: {join_type})")
            
            df = df.merge(df_next, on=join_col, how=join_type)
            print(f"After join. Shape: {df.shape}")
    
    return df

def apply_column_types(df, config):
    """Apply type conversions based on config"""
    columns_config = config.get('columns', {})
    list_columns = []  # Track which columns should be lists
    
    for col, settings in columns_config.items():
        if col not in df.columns:
            continue
            
        col_type = settings.get('type')
        print(f"Converting {col} to {col_type}")
        
        try:
            if col_type == 'datetime':
                df[col] = pd.to_datetime(df[col], errors='coerce')
                
            elif col_type == 'array_of_strings':
                delimiter = settings.get('delimiter', ',')
                # Split strings into lists
                df[col] = df[col].astype(str).apply(
                    lambda x: x.split(delimiter) if x != 'nan' else []
                )
                df[col] = df[col].apply(
                    lambda x: [s.strip() for s in x] if x else []
                )
                list_columns.append(col)  # Mark as list column
                
            elif col_type == 'category':
                df[col] = df[col].astype('category')
                
            elif col_type in ['int32', 'int64']:
                df[col] = pd.to_numeric(df[col], errors='coerce').astype(col_type)
                
            elif col_type in ['float32', 'float64']:
                df[col] = pd.to_numeric(df[col], errors='coerce').astype(col_type)
                
            elif col_type == 'string':
                df[col] = df[col].astype('string')
                
        except Exception as e:
            print(f"Warning: Could not convert {col} to {col_type}: {e}")

    
    # Apply default type to remaining object columns
    default_type = config.get('default_type', 'string')
    for col in df.columns:
        if df[col].dtype == 'object' and col not in columns_config:
            print(f"Converting {col} to default type: {default_type}")
            df[col] = df[col].astype(default_type)
    
    return df, list_columns  # Return both df and list columns


def convert_csv_to_parquet(config_path, data_dir, parquet_file):
    try:
        # Load configuration
        print(f"Loading config from: {config_path}")
        config = load_config(config_path)
        
        # Get CSV files from config
        csv_files = config.get('file_names', [])
        if not csv_files:
            raise ValueError("No file_names specified in config")
        
        print(f"CSV files to process: {csv_files}")
        
        # Get join configuration
        join_config = config.get('join', {'type': 'left', 'column': None})
        
        # Join CSVs
        df = join_csvs(csv_files, data_dir, join_config)
        
        # Apply column name mappings
        df = apply_column_mapping(df, config)
        
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        print(f"\nFinal joined DataFrame shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
        
        # Apply type conversions from config
        print("\nApplying column type conversions...")
        df, list_columns = apply_column_types(df, config)
        
        # Write to Parquet with explicit schema for list columns
        print(f"\nWriting to Parquet file: {parquet_file}")
        
        # First convert to PyArrow table to let it infer types
        table = pa.Table.from_pandas(df)
        
        # Now rebuild schema with explicit list types for array columns
        new_fields = []
        for field in table.schema:
            if field.name in list_columns:
                # Override with list<string> type
                new_fields.append(pa.field(field.name, pa.list_(pa.string())))
            else:
                # Keep the inferred type
                new_fields.append(field)
        
        new_schema = pa.schema(new_fields)
        
        # Rebuild table with new schema for list columns
        arrays = []
        for field in new_schema:
            if field.name in list_columns:
                # Convert Python lists to PyArrow list arrays
                col_data = df[field.name].tolist()
                arrays.append(pa.array(col_data, type=pa.list_(pa.string())))
            else:
                # Use the original column from the table
                arrays.append(table.column(field.name))
        
        table = pa.Table.from_arrays(arrays, schema=new_schema)
        
        pq.write_table(table, parquet_file, compression='snappy')
        
        file_size_mb = Path(parquet_file).stat().st_size / (1024 * 1024)
        print(f"Conversion complete! Parquet file size: {file_size_mb:.2f} MB")
        
        print("\nFirst few rows of the data:")
        print(df.head())
        
        print("\nData types:")
        print(df.dtypes)
        
        # Verify list columns in parquet
        print("\nVerifying list columns in parquet:")
        for field in table.schema:
            if field.name in list_columns:
                print(f"  {field.name}: {field.type}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
if __name__ == "__main__":
    config_path = "data/config/model.json"
    data_dir = "data"
    parquet_file = "public/lv_export.parquet"
    
    convert_csv_to_parquet(config_path, data_dir, parquet_file)