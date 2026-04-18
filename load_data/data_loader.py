import duckdb
import os

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "retail_sales.duckdb")

# Single shared connection (important for Dash/Gunicorn)
def get_connection():
    return duckdb.connect(DB_PATH, read_only=True)

# ----------------------------
# INIT DATABASE (RUN ONCE)
# ----------------------------
def init_db():
    con = get_connection()
    con.execute("""
        CREATE VIEW IF NOT EXISTS retail_sales_v AS
        SELECT
            *,
            CAST(sales AS DOUBLE) * CAST(price AS DOUBLE) AS total_sales,
            EXTRACT(YEAR FROM date) AS year
        FROM retail_sales;
    """)

# ----------------------------
# MAIN DATA ACCESS
# ----------------------------
def get_data():
    con = get_connection()
    return con.execute("SELECT * FROM retail_sales_v").df()


# ----------------------------
# INITIAL FILTER VALUES
# ----------------------------
def get_initial_data():
    con = get_connection()
    return con.execute("""
        SELECT DISTINCT store_id
        FROM retail_sales
        ORDER BY store_id
    """).df()


# ----------------------------
# FILTERED QUERY
# ----------------------------
def get_filtered_sales(stores=None, items=None, start_date=None, end_date=None):
    con = get_connection()
    query = """
        SELECT
            date,
            store_id,
            item_id,
            SUM(total_sales) AS total_sales
        FROM retail_sales_v
        WHERE 1=1
    """

    params = []

    if start_date and end_date:
        query += " AND date BETWEEN ? AND ?"
        params.extend([start_date, end_date])

    if stores:
        query += f" AND store_id IN ({','.join(['?'] * len(stores))})"
        params.extend(stores)

    if items:
        query += f" AND item_id IN ({','.join(['?'] * len(items))})"
        params.extend(items)

    query += """
        GROUP BY date, store_id, item_id
        ORDER BY date
    """

    return con.execute(query, params).df()


# ----------------------------
# ITEM OPTIONS
# ----------------------------
def get_item_options(stores=None):
    con = get_connection()
    query = """
        SELECT DISTINCT item_id
        FROM retail_sales
        WHERE 1=1
    """

    params = []

    if stores:
        query += f" AND store_id IN ({','.join(['?'] * len(stores))})"
        params.extend(stores)

    return con.execute(query, params).df()