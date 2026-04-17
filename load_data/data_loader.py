import os
import pandas as pd
from functools import lru_cache
from kaggle.api.kaggle_api_extended import KaggleApi
import pyarrow

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_PATH = os.path.join(BASE_DIR, "data", "retail_sales.csv")
PARQUET_PATH = os.path.join(BASE_DIR, "data", "retail_sales.parquet")

def ensure_data_exists():
    os.makedirs("data", exist_ok=True)

    if os.path.exists(PARQUET_PATH):
        return

    if not os.path.exists(DATA_PATH):
        api = KaggleApi()
        api.authenticate()
        api.dataset_download_files("dhrubangtalukdar/store-item-demand-forecasting-dataset", path="data", unzip=True)

        print("BASE_DIR:", BASE_DIR)
        print("CSV PATH:", DATA_PATH, os.path.exists(DATA_PATH))
        print("PARQUET PATH:", PARQUET_PATH, os.path.exists(PARQUET_PATH))

@lru_cache(maxsize=1)
def get_data():
    ensure_data_exists()
    
    if os.path.exists(PARQUET_PATH):
        return pd.read_parquet(PARQUET_PATH)
    
    df = pd.read_csv(DATA_PATH)

    # change columns to their right data type
    df["date"] = pd.to_datetime(df['date'])

    # change object columns to numerical
    cols_to_num = ['sales','price','promo','weekday','month']

    df[cols_to_num] = df[cols_to_num].apply(pd.to_numeric, errors = 'coerce')

    # change object columns to string 
    df[['store_id', 'item_id']] = df[['store_id','item_id']].fillna("").astype(str)

    # create a total sales column
    df['total_sales'] = df['sales'] * df['price']

    # create a year column
    df['year'] = df['date'].dt.year

    df['store_id'] = df['store_id'].astype('category')
    df['item_id'] = df['item_id'].astype('category')

    df.to_parquet(PARQUET_PATH, index=False)

    return df