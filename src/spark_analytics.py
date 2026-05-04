import os
import sys
from pathlib import Path
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.window import Window

# Set Python paths at module level to ensure Spark workers find the correct executable
# This must happen BEFORE the SparkSession is created
os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

from config import logger, RAW_DATA_DIR, PROCESSED_DATA_DIR

class SalesAnalytics:
    """
    Performs high-performance sales analytics on e-commerce data using PySpark.
    """

    def __init__(self):
        """Initializes the SalesAnalytics class and starts a Spark Session."""
        self.spark = self.create_spark_session()
        logger.info("SalesAnalytics initialized and Spark Session started.")

    def create_spark_session(self) -> SparkSession:
        """
        Configures and returns a SparkSession optimized for local analytics.
        - Memory: 4GB
        - AQE: Enabled
        - Serializer: Kryo
        """
        return SparkSession.builder \
            .appName("EcommerceSalesAnalytics") \
            .master("local[*]") \
            .config("spark.driver.memory", "4g") \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
            .getOrCreate()

    def load_data(self, base_path: Path, filename_stem: str) -> DataFrame:
        """
        Loads data from Parquet if available, falling back to CSV.

        Args:
            base_path: Directory containing the data.
            filename_stem: The filename without extension (e.g., 'products').

        Returns:
            DataFrame: Loaded Spark DataFrame.
        """
        parquet_path = base_path / f"{filename_stem}.parquet"
        csv_path = base_path / f"{filename_stem}.csv"

        if parquet_path.exists():
            logger.info(f"Loading Parquet: {parquet_path}")
            return self.spark.read.parquet(str(parquet_path.absolute()))
        elif csv_path.exists():
            logger.info(f"Loading CSV: {csv_path}")
            return self.spark.read.option("header", "true").option("inferSchema", "true").csv(str(csv_path.absolute()))
        else:
            raise FileNotFoundError(f"No data file found for {filename_stem} in {base_path}")

    def top_customers_by_revenue(self, orders_df: DataFrame, products_df: DataFrame, 
                                 n: int = 10) -> DataFrame:
        """
        Calculates total spend per customer and returns top N.

        Args:
            orders_df: Spark DataFrame containing order records.
            products_df: Spark DataFrame containing product records.
            n: Number of top customers to return.

        Returns:
            DataFrame: Top customers by total spend.
        """
        # Calculate line totals and aggregate by customer_id
        # Using broadcast join as products is likely much smaller than orders
        return orders_df.join(F.broadcast(products_df), "product_id") \
            .withColumn("revenue", F.round(F.col("quantity") * F.col("price"), 2)) \
            .groupBy("customer_id") \
            .agg(F.sum("revenue").alias("total_spend")) \
            .orderBy(F.desc("total_spend")) \
            .limit(n)

    def sales_by_category(self, orders_df: DataFrame, products_df: DataFrame) -> DataFrame:
        """
        Groups by product category, sums revenue and units sold.

        Args:
            orders_df: Spark DataFrame containing order records.
            products_df: Spark DataFrame containing product records.

        Returns:
            DataFrame: Sales metrics aggregated by category.
        """
        return orders_df.join(F.broadcast(products_df), "product_id") \
            .withColumn("revenue", F.col("quantity") * F.col("price")) \
            .groupBy("category") \
            .agg(
                F.sum("revenue").alias("total_revenue"),
                F.sum("quantity").alias("units_sold")
            ).orderBy(F.desc("total_revenue"))

    def monthly_trends(self, orders_df: DataFrame, products_df: DataFrame) -> DataFrame:
        """
        Calculates month-over-month revenue growth percentage using Window functions.

        Args:
            orders_df: Spark DataFrame containing order records.
            products_df: Spark DataFrame containing product records.

        Returns:
            DataFrame: Monthly revenue and growth percentage.
        """
        # Calculate monthly revenue
        monthly_rev = orders_df.join(F.broadcast(products_df), "product_id") \
            .withColumn("month", F.date_format("order_date", "yyyy-MM")) \
            .groupBy("month") \
            .agg(F.sum(F.col("quantity") * F.col("price")).alias("revenue"))

        # Window function for growth calculation
        window_spec = Window.orderBy("month")
        df_growth = monthly_rev.withColumn("prev_rev", F.lag("revenue").over(window_spec))
        
        return df_growth.withColumn(
            "growth_pct", 
            F.when(F.col("prev_rev").isNull() | (F.col("prev_rev") == 0), 0)
            .otherwise(F.round(((F.col("revenue") - F.col("prev_rev")) / F.col("prev_rev")) * 100, 2))
        ).select("month", "revenue", "growth_pct") \
            .orderBy("month")

    def run_all(self):
        """Orchestrates the loading, processing, and saving of analytics."""
        try:
            # Load data (handles both CSV and Parquet)
            products = self.load_data(RAW_DATA_DIR, "products")
            orders = self.load_data(RAW_DATA_DIR, "orders")

            # Process analytics
            top_cust = self.top_customers_by_revenue(orders, products)
            cat_sales = self.sales_by_category(orders, products)
            trends = self.monthly_trends(orders, products)

            # Display results
            print("\n--- Top Customers ---")
            top_cust.show()
            print("\n--- Sales by Category ---")
            cat_sales.show()
            print("\n--- Monthly Trends ---")
            trends.show()
            
            # Save results
            PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
            trends.write.mode("overwrite").parquet(str((PROCESSED_DATA_DIR / "monthly_trends.parquet").absolute()))
            
            logger.info("Analysis successfully completed and saved.")
        except Exception as e:
            logger.error(f"Analysis failed: {e}", exc_info=True)
        finally:
            self.spark.stop()

if __name__ == "__main__":
    analytics = SalesAnalytics()
    analytics.run_all()