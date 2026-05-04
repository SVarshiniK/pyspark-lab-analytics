import pandas as pd
import numpy as np
import logging
from faker import Faker
from tqdm import tqdm
from typing import Tuple, List
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SyntheticDataGenerator:
    """
    Generates synthetic e-commerce data including customers, products, and orders
    using realistic statistical distributions.
    """

    def __init__(self, seed: int = 42):
        """Initializes the generator with a random seed for reproducibility."""
        self.fake = Faker()
        Faker.seed(seed)
        np.random.seed(seed)
        self.categories = ['Electronics', 'Clothing', 'Home', 'Sports', 'Books']

    def generate_customers(self, n: int = 100_000) -> pd.DataFrame:
        """
        Generates customer data. Age follows a normal distribution around 35.
        """
        logger.info(f"Generating {n} customers...")
        
        customers = []
        # Pre-generate ages using normal distribution
        ages = np.random.normal(loc=35, scale=10, size=n).astype(int)
        ages = np.clip(ages, 18, 90)  # Ensure realistic age range

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

    def generate_products(self, n: int = 10_000) -> pd.DataFrame:
        """
        Generates product data with random prices and stock levels.
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

    def generate_orders(self, 
                        n_orders: int = 1_000_000, 
                        customer_ids: List[int] = None, 
                        product_ids: List[int] = None) -> pd.DataFrame:
        """
        Generates order data. Uses Pareto distribution to ensure 20% of 
        customers account for roughly 80% of orders.
        """
        if not customer_ids or not product_ids:
            raise ValueError("customer_ids and product_ids must be provided.")

        logger.info(f"Generating {n_orders} orders...")

        # Pareto distribution logic: create weights for customers
        # a=1.16 approximates the 80/20 rule
        weights = np.random.pareto(1.16, len(customer_ids))
        weights /= weights.sum()

        orders = []
        # Vectorized selection for performance
        chosen_customers = np.random.choice(customer_ids, size=n_orders, p=weights)
        chosen_products = np.random.choice(product_ids, size=n_orders)
        quantities = np.random.randint(1, 11, size=n_orders)

        for i in tqdm(range(n_orders), desc="Orders"):
            orders.append({
                "order_id": i + 1,
                "customer_id": chosen_customers[i],
                "product_id": chosen_products[i],
                "quantity": int(quantities[i]),
                "order_date": self.fake.date_time_between(start_date='-1y', end_date='now')
            })

        return pd.DataFrame(orders)

    def run_and_save(self, 
                     cust_count: int = 100_000, 
                     prod_count: int = 10_000, 
                     order_count: int = 1_000_000,
                     output_path: str = "../data/raw/"):
        """
        Executes the full generation process and saves to CSV.
        """
        df_customers = self.generate_customers(cust_count)
        df_products = self.generate_products(prod_count)
        
        df_orders = self.generate_orders(
            order_count, 
            customer_ids=df_customers['customer_id'].tolist(),
            product_ids=df_products['product_id'].tolist()
        )

        logger.info("Saving datasets to disk...")
        df_customers.to_csv(f"{output_path}customers.csv", index=False)
        df_products.to_csv(f"{output_path}products.csv", index=False)
        df_orders.to_csv(f"{output_path}orders.csv", index=False)
        logger.info("Generation complete.")

if __name__ == "__main__":
    generator = SyntheticDataGenerator()
    generator.run_and_save()