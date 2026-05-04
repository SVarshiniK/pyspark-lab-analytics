import time
import os
from pathlib import Path
import pandas as pd
from src.data_generator import SyntheticDataGenerator
from src.config import logger, RAW_DATA_DIR, NUM_CUSTOMERS, NUM_PRODUCTS, NUM_ORDERS

def format_file_size(path: Path) -> str:
    """
    Calculates and formats file size in human-readable units.

    Args:
        path: Path object to the file.

    Returns:
        str: Formatted size (e.g., '12.34 MB').
    """
    size = path.stat().st_size
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"

def main() -> None:
    """
    Orchestrates the data generation process.
    1. Initializes the generator.
    2. Generates customers, products, and orders using specified counts.
    3. Saves data as Parquet files for optimized storage/retrieval.
    4. Reports metrics including row counts, file sizes, and execution time.
    """
    start_time = time.time()
    logger.info("Initializing synthetic data generation pipeline...")
    
    try:
        # Initialize the generator
        generator = SyntheticDataGenerator()
        
        # Generate datasets
        df_customers = generator.generate_customers(NUM_CUSTOMERS)
        df_products = generator.generate_products(NUM_PRODUCTS)
        df_orders = generator.generate_orders(
            NUM_ORDERS, 
            customer_ids=df_customers["customer_id"].tolist(), 
            product_ids=df_products["product_id"].tolist()
        )
        
        # Mapping of filenames to dataframes for batch processing
        datasets = {
            "customers.parquet": df_customers,
            "products.parquet": df_products,
            "orders.parquet": df_orders
        }
        
        print("\n" + "="*60)
        print(f"{'Dataset':<20} | {'Rows':<12} | {'File Size':<15}")
        print("-" * 60)
        
        for filename, df in datasets.items():
            file_path = RAW_DATA_DIR / filename
            
            # Save to Parquet format (requires pyarrow or fastparquet)
            df.to_parquet(file_path, index=False)
            
            # Report metrics
            size_str = format_file_size(file_path)
            print(f"{filename:<20} | {len(df):<12,d} | {size_str:<15}")
            
        end_time = time.time()
        print("="*60)
        print(f"Pipeline completed in {end_time - start_time:.2f} seconds.")
        logger.info("Data generation pipeline completed successfully.")

    except Exception as e:
        logger.error(f"Data pipeline failed: {e}", exc_info=True)
        print(f"\n[ERROR] Pipeline failed. See log for details: {e}")

if __name__ == "__main__":
    main()