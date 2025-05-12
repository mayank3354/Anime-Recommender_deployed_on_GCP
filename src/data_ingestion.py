import os
import pandas as pd
from google.cloud import storage
from src.logger import get_logger
import src.custon_exception as ce
import sys
from config.paths_config import RAW_DIR, CONFIG_PATH
from utils.common_functions import read_yaml_file

lg = get_logger(__name__)

class DataIngestion:
    def __init__(self, config: dict):
        self.config = config["data_ingestion"]
        self.bucket_name = self.config["bucket_name"]
        self.file_names = self.config["bucket_file_name"]
        
        os.makedirs(RAW_DIR, exist_ok=True)

        lg.info("Data ingestion class initialized")


    def download_csv_from_gcp(self):
        try:
            lg.info("Downloading file from GCS")
            client = storage.Client()
            bucket = client.bucket(self.bucket_name)
            for file_name in self.file_names:
                file_path = os.path.join(RAW_DIR, file_name)
                if file_name=="animelist.csv":
                    blob = bucket.blob(file_name)
                    blob.download_to_filename(file_path)

                    data = pd.read_csv(file_path, nrows=5000000)
                    data.to_csv(file_path, index=False)
                    lg.info(f"Large File {file_name} only 5 Million rows downloaded successfully")

                else:
                    blob = bucket.blob(file_name)
                    blob.download_to_filename(file_path)
                    lg.info(f"Downloading smaller files ie anime and anime sypnosis")

                lg.info("File downloaded successfully")
        except Exception as e:
            lg.error(f"Error downloading file from GCS: {e}")
            raise ce.CustomException(e, sys) from e
        
    def run(self):
        try:
            lg.info("Starting data ingestion")
            self.download_csv_from_gcp()
            lg.info("Data ingestion completed")
        except Exception as ce:
            lg.error(f"Error in data ingestion: {str(ce)}")
            
        finally:
            lg.info("Data ingestion DONE......")

if __name__ == "__main__":
    config = read_yaml_file(CONFIG_PATH)
    data_ingestion = DataIngestion(config)
    data_ingestion.run()

