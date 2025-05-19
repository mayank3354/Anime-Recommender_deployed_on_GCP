from src.model_training import ModelTraining
from config.paths_config import *
from src.data_ingestion import DataIngestion
from utils.common_functions import read_yaml_file    
from src.data_processing import DataProcessing

if __name__ == "__main__":
    

    data_processing = DataProcessing(input_file=ANIMELIST_CSV, output_dir=PROCESSED_DIR)
    data_processing.run()
    
    model_training = ModelTraining(data_path=PROCESSED_DIR)
    model_training.train_model()

