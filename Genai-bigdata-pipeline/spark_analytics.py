from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from config import logger, CUSTOMERS_FILE, PRODUCTS_FILE, ORDERS_FILE, PROCESSED_DATA_DIR

def get_spark_session() -> SparkSession:
    """
    Initializes and returns a SparkSession.

    Returns:
        SparkSession: The entry point to Spark functionality.
    """
    return SparkSession.builder \
        .appName("EcommerceAnalytics") \
        .getOrCreate()

def run_analysis() -> None:
    """
    Loads raw CSV data, performs aggregations, and saves results to parquet.
    """
    spark = None
    try:
        spark = get_spark_session()
        logger.info("Spark Session started.")

        # Load Data
        logger.info("Loading raw data into Spark DataFrames...")
        customers = spark.read.csv(CUSTOMERS_FILE.as_uri(), header=True, inferSchema=True)
        products = spark.read.csv(PRODUCTS_FILE.as_uri(), header=True, inferSchema=True)
        orders = spark.read.csv(ORDERS_FILE.as_uri(), header=True, inferSchema=True)

        # Join Data
        logger.info("Joining datasets...")
        order_details = orders.join(products, "product_id") \
                             .join(customers, "customer_id")

        # Calculate Revenue per Order Line
        order_details = order_details.withColumn("line_total", F.col("quantity") * F.col("price"))

        # 1. Top Categories by Revenue
        logger.info("Analyzing top categories...")
        category_analysis = order_details.groupBy("category") \
            .agg(
                F.sum("line_total").alias("total_revenue"),
                F.count("order_id").alias("order_count")
            ) \
            .orderBy(F.desc("total_revenue"))

        # 2. Customer Spending Analysis
        logger.info("Analyzing customer spending...")
        customer_spending = order_details.groupBy("customer_id", "name") \
            .agg(F.sum("line_total").alias("total_spent")) \
            .orderBy(F.desc("total_spent"))

        # Save Results
        output_path = PROCESSED_DATA_DIR / "category_revenue"
        category_analysis.write.mode("overwrite").parquet(output_path.as_uri())
        
        # Show Sample Results
        print("\n--- Top Categories ---")
        category_analysis.show(5)

        print("\n--- Top Customers ---")
        customer_spending.show(5)

        logger.info(f"Analysis complete. Results saved in {PROCESSED_DATA_DIR}")

    except Exception as e:
        logger.error(f"Error during Spark analysis: {e}")
        raise
    finally:
        if spark:
            spark.stop()
            logger.info("Spark Session stopped.")

if __name__ == "__main__":
    # Ensure data exists before running analysis
    import os
    if not os.path.exists(ORDERS_FILE):
        logger.error("Raw data files not found. Run data_generator.py first.")
    else:
        run_analysis()