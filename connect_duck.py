import duckdb

con = duckdb.connect('./data/health_care_fraud.duckdb')

con.execute("""
            CREATE TABLE healthcare_fraud AS 
            SELECT * FROM read_csv_auto('data/healthcare_fraud_detection.csv')
            """)