import os 
os.environ['KAGGLE_USERNAME'] = "kcastaneda"
os.environ['KAGGLE_KEY'] = "KGAT_8dd490520c2a18b9e37962ad0c7efaeb"

from kaggle.api.kaggle_api_extended import KaggleApi
api= KaggleApi()
api.authenticate()


api.dataset_download_files("nudratabbas/healthcare-fraud-detection-dataset" path="./data")

import zipfile

zip_path = "./data/healthcare-fraud-detection-dataset.zip"

with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall("./data")