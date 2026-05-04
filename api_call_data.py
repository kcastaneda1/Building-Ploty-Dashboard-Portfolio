import os 
os.environ['KAGGLE_USERNAME'] = "kcastaneda"
os.environ['KAGGLE_KEY'] = "KGAT_8dd490520c2a18b9e37962ad0c7efaeb"

from kaggle.api.kaggle_api_extended import KaggleApi
api= KaggleApi()
api.authenticate()

DATA_PATH = 'data'

import os
if not os.path.exists(DATA_PATH):
    # download dataset only once
    api.dataset_download_files('nudratabbas/healthcare-fraud-detection-dataset'
                               , path=DATA_PATH
                               ,unzip=True
    )