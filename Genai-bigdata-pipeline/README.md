# E-commerce Data Pipeline

This project simulates an e-commerce data environment. It generates synthetic customer, product, and order data and performs business intelligence analysis using PySpark.

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Generate Data**:
   Run the data generator to create raw CSV files in `data/raw/`.
   ```bash
   python src/data_generator.py
   ```

3. **Run Analytics**:
   Process the raw data using PySpark to find insights.
   ```bash
   python src/spark_analytics.py
   ```

Note: Ensure you have Java installed and `JAVA_HOME` configured for PySpark to run.