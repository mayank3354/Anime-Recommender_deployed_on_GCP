import os
import pandas as pd
from src.logger import get_logger
import src.custon_exception as ce
import yaml
import sys

lg = get_logger(__name__)

def read_yaml_file(file_path: str) -> dict:
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.")
        with open(file_path, "rb") as yaml_file:
            config = yaml.safe_load(yaml_file)
            lg.info(f"Successfully read the yaml file: {file_path}")
            return config
    except Exception as e:
        lg.error(f"Error reading the yaml file: {e}")
        raise ce.CustomException(e, sys) from e
    
    
def load_data(file_path: str, schema_file_path: str) -> pd.DataFrame:
    try:
        lg.info(f"Loading data from {file_path}")
        dataframe = pd.read_csv(file_path)
        lg.info(f"Data loaded successfully from {file_path}")
        return dataframe
    except Exception as e:
        lg.error(f"Error loading data from {file_path}: {e}")
        raise ce.CustomException(e, sys) from e
