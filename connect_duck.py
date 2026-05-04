import duckdb

with duckdb.connect('health_care_fraud.duckdb') as con:
    con.execute("""
            CREATE TABLE healthcare_fraud AS 
            SELECT * FROM read_csv_auto('data/healthcare_fraud_detection.csv')
            """)