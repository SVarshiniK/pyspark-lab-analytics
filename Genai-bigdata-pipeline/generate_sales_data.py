import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_sales_dataset(output_path: str, num_rows: int = 100000):
    """
    Generates a synthetic sales dataset for EDA practice.
    """
    try:
        # Set seed for reproducibility
        np.random.seed(42)

        print(f"Generating {num_rows} rows of data...")

        # 1. Transaction and Customer IDs
        transaction_ids = np.arange(100001, 100001 + num_rows)
        customer_ids = np.random.randint(1000, 5000, size=num_rows)

        # 2. Products and Categories mapping
        products_config = {
            "Electronics": ["Laptop", "Smartphone", "Monitor", "Headphones", "Tablet"],
            "Furniture": ["Desk Chair", "Bookshelf", "Office Desk", "Lamp"],
            "Appliances": ["Coffee Maker", "Toaster", "Microwave", "Blender"],
            "Clothing": ["T-Shirt", "Jeans", "Jacket", "Sneakers"]
        }
        
        # Flatten the categories and products for random selection
        categories_list = list(products_config.keys())
        random_categories = np.random.choice(categories_list, size=num_rows)
        random_products = [np.random.choice(products_config[cat]) for cat in random_categories]

        # 3. Quantity and Price
        quantity = np.random.randint(1, 11, size=num_rows)
        # Base prices between 15.0 and 1500.0
        price = np.round(np.random.uniform(15.0, 1500.0, size=num_rows), 2)

        # Introduce 5% missing values in the 'price' column
        price_nan_indices = np.random.choice(num_rows, size=int(num_rows * 0.05), replace=False)
        price[price_nan_indices] = np.nan

        # 4. Revenue (Quantity * Price)
        revenue = np.round(quantity * price, 2)

        # 5. Date range (2023 to 2024)
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2024, 12, 31)
        delta_days = (end_date - start_date).days
        random_days = np.random.randint(0, delta_days, size=num_rows)
        dates = [start_date + timedelta(days=int(d)) for d in random_days]

        # 6. Regions
        regions_list = ["North America", "Europe", "Asia-Pacific", "LATAM", "EMEA"]
        # Convert to object type to allow None/NaN assignment
        region = np.random.choice(regions_list, size=num_rows).astype(object)

        # Introduce 2% missing values in the 'region' column
        region_nan_indices = np.random.choice(num_rows, size=int(num_rows * 0.02), replace=False)
        region[region_nan_indices] = np.nan

        # Build DataFrame
        df = pd.DataFrame({
            "transaction_id": transaction_ids,
            "customer_id": customer_ids,
            "product": random_products,
            "category": random_categories,
            "quantity": quantity,
            "price": price,
            "revenue": revenue,
            "date": dates,
            "region": region
        })

        # Save to CSV
        df.to_csv(output_path, index=False)
        print(f"Success! Dataset saved to: {os.path.abspath(output_path)}")
        print(f"Total Rows: {len(df)}")

    except Exception as e:
        print(f"An error occurred during data generation: {e}")

if __name__ == "__main__":
    FILE_NAME = "Supermarket_Sales.csv"
    generate_sales_dataset(FILE_NAME)