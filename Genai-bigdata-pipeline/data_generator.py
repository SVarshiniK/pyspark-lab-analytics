import pandas as pd
from faker import Faker
import random
from typing import List
from config import logger, CUSTOMERS_FILE, PRODUCTS_FILE, ORDERS_FILE, NUM_CUSTOMERS, NUM_PRODUCTS, NUM_ORDERS

fake = Faker()

def generate_customers(num_rows: int) -> pd.DataFrame:
    """
    Generates a synthetic customer dataset.

    Args:
        num_rows: The number of customers to generate.

    Returns:
        pd.DataFrame: Customer data with ID, name, and email.
    """
    logger.info(f"Generating {num_rows} customers...")
    customers = []
    for i in range(1, num_rows + 1):
        customers.append({
            "customer_id": i,
            "name": fake.name(),
            "email": fake.email(),
            "country": fake.country()
        })
    return pd.DataFrame(customers)

def generate_products(num_rows: int) -> pd.DataFrame:
    """
    Generates a synthetic product dataset.

    Args:
        num_rows: The number of products to generate.

    Returns:
        pd.DataFrame: Product data with ID, category, and price.
    """
    logger.info(f"Generating {num_rows} products...")
    categories = ["Electronics", "Clothing", "Home & Garden", "Books", "Toys"]
    products = []
    for i in range(1, num_rows + 1):
        products.append({
            "product_id": i,
            "product_name": f"Product_{i}",
            "category": random.choice(categories),
            "price": round(random.uniform(10.0, 500.0), 2)
        })
    return pd.DataFrame(products)

def generate_orders(num_rows: int, customer_ids: List[int], product_ids: List[int]) -> pd.DataFrame:
    """
    Generates a synthetic orders dataset linking customers and products.

    Args:
        num_rows: Number of orders to create.
        customer_ids: List of valid customer IDs.
        product_ids: List of valid product IDs.

    Returns:
        pd.DataFrame: Order data with ID, relations, and quantities.
    """
    logger.info(f"Generating {num_rows} orders...")
    orders = []
    for i in range(1, num_rows + 1):
        orders.append({
            "order_id": 10000 + i,
            "customer_id": random.choice(customer_ids),
            "product_id": random.choice(product_ids),
            "quantity": random.randint(1, 5),
            "order_date": fake.date_between(start_date='-1y', end_date='today')
        })
    return pd.DataFrame(orders)

def run_generator() -> None:
    """
    Main execution function to generate all datasets and save to CSV.
    """
    try:
        # Generate
        df_customers = generate_customers(NUM_CUSTOMERS)
        df_products = generate_products(NUM_PRODUCTS)
        df_orders = generate_orders(
            NUM_ORDERS, 
            df_customers["customer_id"].tolist(), 
            df_products["product_id"].tolist()
        )

        # Save
        df_customers.to_csv(CUSTOMERS_FILE, index=False)
        df_products.to_csv(PRODUCTS_FILE, index=False)
        df_orders.to_csv(ORDERS_FILE, index=False)

        logger.info(f"Success! Data saved to {CUSTOMERS_FILE.parent}")

    except Exception as e:
        logger.error(f"Error during data generation: {e}")
        raise

if __name__ == "__main__":
    run_generator()