# E-commerce Data Pipeline

This project simulates an e-commerce data environment. It generates synthetic customer, product, and order data using `Faker` and performs business intelligence analysis using `PySpark`.

## Project Structure
- `src/`: Core Python logic.
- `data/raw/`: Generated CSV datasets.
- `data/processed/`: Analysis output in Parquet format.
- `tests/`: Unit tests.
- `notebooks/`: Data exploration.

## Setup and Usage

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Generate Synthetic Data**:
   ```bash
   python src/data_generator.py
   ```

3. **Run Analytics**:
   ```bash
   python src/spark_analytics.py
   ```

## Prerequisites
- Python 3.9+
- Java 8 or 11 (required for PySpark)