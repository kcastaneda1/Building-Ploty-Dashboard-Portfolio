import requests
import pandas as pd

base_url = "https://data.medicaid.gov/api/1/datastore/query/6165f45b-ca93-5bb5-9d06-db29c692a360/0"

def get_medicaid_data(limit=100):
    """
    Retrieve all medicaid data Centers for Medicare & Medicaid Services (CMS) API.
    Data is retrieved in batches using limit/offset pagination.
    The function will continue to retrieve data untill no more data is available.
    """

    all_records = []
    offset = 0

    while True:
        params ={
            'limit':limit,
            'offset':offset
        }

        try:
            response = requests.get(base_url, params= params, timeout=30)
            response.raise_for_status() # Raise an exception for HTTP errors
        except requests.RequestException as e:
            raise RuntimeError(
                f"CMS Medicaid API request failed"
                f" a offset {offset}: {e}"
            ) from e 

        data = response.json()
        records = data.get("results",[])

        #Stop when the API return no records
        if not records:
            break

        all_records.extend(records)
        offset += len(records) #Increment the offset by the number of records retrieved

        if len(records) < limit:
            break #Stop if the number of records retrieved is less than the limit, indicating no more data is available

    return pd.DataFrame(all_records) #Return a DataFrame containing all retrieved records

