from kaggle.api.kaggle_api_extended import KaggleApi
import os

api= KaggleApi()
api.authenticate()

DATA_PATH = 'data'

if not os.path.exists(DATA_PATH):
    # download dataset only once
    api.dataset_download_files(
        "nudratabbas/healthcare-fraud-detection-dataset',
        path=DATA_PATH,
        unzip=True
    )