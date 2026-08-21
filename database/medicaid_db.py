import duckdb as db
from formatting.medicaid_raw import clean_dataset

DB_PATH = 'data/medicaid.duckdb'

def get_connection_medicaid():
    return db.connect(DB_PATH)

def create_medicaid_raw_table(con):
    df = clean_dataset()
    con.register("medicaid_df", df)

    con.execute("""
    CREATE OR REPLACE TABLE medicaid_raw as 
    SELECT *
    FROM medicaid_df
    """)

    con.unregister("medicaid_df")

def create_medicaid_analytics_view(con):
    con.execute("""
    CREATE OR REPLACE VIEW medicaid_analytics AS 
    SELECT 
        *,
        CASE 
            WHEN final_report = 'Y'
            THEN TRUE
            ELSE FALSE
        END AS is_final_record,
        CASE 
            WHEN preliminary_or_updated = 'P'
            THEN 'Preliminary'
            WHEN preliminary_or_updated = 'U'
            THEN 'Updated'
            ELSE 'Unknown'
        END AS reporting_version
    FROM medicaid_raw
    """)

def create_medicaid_final_view(con):
    con.execute("""
    CREATE OR REPLACE VIEW medicaid_final AS 
    SELECT 
        *
    FROM medicaid_analytics
    WHERE is_final_record = TRUE
    """)

def create_latest_state_enrollment_view(con):
    con.execute("""
    CREATE OR REPLACE VIEW vw_lastest_state_enrollment AS 
    SELECT 
        state_abbreviation,
        state_name,
        reporting_date,
        total_medicaid_and_chip_enrollment,
        total_medicaid_enrollment,
        total_chip_enrollment,
        total_adult_medicaid_enrollment 
    FROM medicaid_final 
    QUALIFY ROW_NUMBER() OVER(PARTITION BY state_abbreviation ORDER BY reporting_date DESC) = 1
    """)

def create_enrollment_trend_view(con):
    con.execute("""
    CREATE OR REPLACE VIEW vw_enrollment_trend AS 
    SELECT 
        reporting_date,
        state_name,
        sum(total_medicaid_and_chip_enrollment) as total_medicaid_chip_enrollment,
        sum(total_medicaid_enrollment) as total_medicaid_enrollment,
        sum(total_chip_enrollment) as total_chip_enrollment
    FROM medicaid_final
    GROUP BY reporting_date, state_name 
    ORDER BY reporting_date
    """)

def create_state_enrollment_growth_view(con):
    con.execute("""
    CREATE OR REPLACE VIEW vw_state_enrollment_growth AS 
    SELECT 
        *,
        CASE 
            WHEN previous_enrollment IS NULL or previous_enrollment = 0
            THEN NULL
            ELSE (enrollment_change / previous_enrollment) * 100 END AS enrollment_pct_change
    FROM (
        SELECT 
            state_abbreviation,
            state_name,
            reporting_date,
            total_medicaid_and_chip_enrollment,
            LAG(total_medicaid_and_chip_enrollment) OVER(PARTITION BY state_abbreviation ORDER BY reporting_date) AS previous_enrollment,
            (total_medicaid_and_chip_enrollment - 
                LAG(total_medicaid_and_chip_enrollment) OVER(PARTITION BY state_abbreviation ORDER BY reporting_date)) AS enrollment_change
        FROM medicaid_final
    )
    """)

def create_latest_state_growth_view(con):
    con.execute("""
    CREATE OR REPLACE VIEW vw_latest_state_growth AS 
    SELECT 
        state_abbreviation,
        state_name,
        reporting_date,
        total_medicaid_and_chip_enrollment,
        previous_enrollment,
        enrollment_change,
        enrollment_pct_change
    FROM vw_state_enrollment_growth 
    QUALIFY ROW_NUMBER() OVER(PARTITION BY state_abbreviation ORDER BY reporting_date DESC) = 1
    """)

def build_medicaid_database():
    con = get_connection_medicaid()
    try:
        create_medicaid_raw_table(con)
        create_medicaid_analytics_view(con)
        create_medicaid_final_view(con)
        create_latest_state_enrollment_view(con)
        create_enrollment_trend_view(con)
        create_state_enrollment_growth_view(con)
        create_latest_state_growth_view(con)
    finally:
        con.close()

#if __name__ == '__main__':
#    build_medicaid_database()