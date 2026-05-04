import pandas as pd
import numpy as np
from faker import Faker
from tqdm import tqdm
from typing import List
from .config import logger, CUSTOMERS_FILE, PRODUCTS_FILE, ORDERS_FILE, NUM_CUSTOMERS, NUM_PRODUCTS, NUM_ORDERS

class SyntheticDataGenerator:
    """
    Generates synthetic e-commerce data including customers, products, and orders
    using realistic statistical distributions.
    """

    def __init__(self, seed: int = 42):
        """
        Initializes the generator with a random seed for reproducibility.
        
        Args:
            seed: Integer seed for numpy and Faker.
        """
        self.fake = Faker()
        Faker.seed(seed)
        np.random.seed(seed)
        self.categories = ['Electronics', 'Clothing', 'Home', 'Sports', 'Books']

    def generate_customers(self, n: int) -> pd.DataFrame:
        """
        Generates customer data. Age follows a normal distribution around 35.

        Args:
            n: Number of customer records to generate.

        Returns:
            pd.DataFrame: Customer records.
        """
        logger.info(f"Generating {n} customers...")
        
        # Pre-generate ages using normal distribution (mean=35, std=10)
        ages = np.random.normal(loc=35, scale=10, size=n).astype(int)
        ages = np.clip(ages, 18, 90)

        customers = []
        for i in tqdm(range(n), desc="Customers"):
            customers.append({
                "customer_id": i + 1,
                "name": self.fake.name(),
                "email": self.fake.unique.email(),
                "age": int(ages[i]),
                "city": self.fake.city(),
                "country": self.fake.country(),
                "registration_date": self.fake.date_between(start_date='-3y', end_date='today')
            })
        return pd.DataFrame(customers)

    def generate_products(self, n: int) -> pd.DataFrame:
        """
        Generates product data with random prices and stock levels.

        Args:
            n: Number of product records to generate.

        Returns:
            pd.DataFrame: Product records.
        """
        logger.info(f"Generating {n} products...")
        
        products = []
        for i in tqdm(range(n), desc="Products"):
            products.append({
                "product_id": i + 1,
                "name": f"Product_{i + 1}",
                "category": np.random.choice(self.categories),
                "price": round(np.random.uniform(10, 500), 2),
                "stock": np.random.randint(0, 1000),
                "rating": round(np.random.uniform(1, 5), 1)
            })
        return pd.DataFrame(products)

    def generate_orders(self, n_orders: int, customer_ids: List[int], product_ids: List[int]) -> pd.DataFrame:
        """
        Generates order data. Uses Pareto distribution to ensure 20% of 
        customers account for roughly 80% of orders.

        Args:
            n_orders: Total number of orders to generate.
            customer_ids: List of available customer IDs.
            product_ids: List of available product IDs.

        Returns:
            pd.DataFrame: Order records.
        """
        logger.info(f"Generating {n_orders} orders...")

        # Pareto distribution (a=1.16) approximates the 80/20 rule
        weights = np.random.pareto(1.16, len(customer_ids))
        weights /= weights.sum()

        # Vectorized selection for high performance
        chosen_customers = np.random.choice(customer_ids, size=n_orders, p=weights)
        chosen_products = np.random.choice(product_ids, size=n_orders)
        quantities = np.random.randint(1, 11, size=n_orders)

        orders = []
        for i in tqdm(range(n_orders), desc="Orders"):
            orders.append({
                "order_id": i + 1,
                "customer_id": int(chosen_customers[i]),
                "product_id": int(chosen_products[i]),
                "quantity": int(quantities[i]),
                "order_date": self.fake.date_time_between(start_date='-1y', end_date='now')
            })
        return pd.DataFrame(orders)

def run_generator() -> None:
    """
    Main execution function to generate all datasets and save to CSV files.
    """
    try:
        generator = SyntheticDataGenerator()
        
        # Generate datasets
        df_customers = generator.generate_customers(NUM_CUSTOMERS)
        df_products = generator.generate_products(NUM_PRODUCTS)
        df_orders = generator.generate_orders(
            NUM_ORDERS, 
            df_customers["customer_id"].tolist(), 
            df_products["product_id"].tolist()
        )

        # Save to raw data directory
        logger.info("Saving datasets to CSV...")
        df_customers.to_csv(CUSTOMERS_FILE, index=False)
        df_products.to_csv(PRODUCTS_FILE, index=False)
        df_orders.to_csv(ORDERS_FILE, index=False)

        logger.info(f"Success! Files saved to {CUSTOMERS_FILE.parent}")

    except Exception as e:
        logger.error(f"Error during data generation: {e}")
        raise

if __name__ == "__main__":
    run_generator()