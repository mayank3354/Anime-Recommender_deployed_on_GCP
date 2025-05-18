import pandas as pd
import numpy as np
import os
import joblib

from sklearn.model_selection import train_test_split
from src.logger import get_logger
from src.custon_exception import CustomException
from config.paths_config import *
import sys



logger = get_logger(__name__)

class DataProcessing:
    def __init__(self,input_file, output_dir):

        self.input_file = input_file
        self.output_dir = output_dir

        self.rating_df = None
        self.anime_df = None
        self.X_train_array = None
        self.X_test_array = None
        self.y_train = None
        self.y_test = None

        self.user2user_encoded = {}
        self.user2user_decoded = {}
        self.anime2anime_encoded = {}
        self.anime2anime_decoded = {}

        os.makedirs(self.output_dir, exist_ok=True)
        logger.info("Data Processing Initialized")

    def load_data(self,usecols):
        try:
            logger.info("Loading data from %s", self.input_file)
            self.rating_df = pd.read_csv(self.input_file,usecols=usecols,low_memory=True)

            logger.info("Data loaded successfully")

        except Exception as e:
            logger.error("Error loading data: %s", e)
            raise CustomException(e,sys)

    def filter_users(self,min_ratings=400):
        try:
            logger.info("Filtering users with minimum ratings: %s", min_ratings)

            user_rating_count = self.rating_df.groupby('user_id')['rating'].count()
            self.rating_df = self.rating_df[self.rating_df['user_id'].isin(user_rating_count[user_rating_count >= min_ratings].index)]

            logger.info("Users filtered successfully")

            
        except Exception as e:
            logger.error("Error filtering users: %s", e)
            raise CustomException(e,sys)

    def scale_ratings(self):
        try:
            logger.info("Scaling ratings")
            min_rating = self.rating_df['rating'].min()
            max_rating = self.rating_df['rating'].max()

            # min max scaler
            self.rating_df["rating"] = self.rating_df["rating"].apply(lambda X: (X - min_rating) / (max_rating - min_rating)).values.astype(np.float64)

            logger.info("Ratings scaled successfully")

            
        except Exception as e:
            logger.error("Error scaling ratings: %s", e)
            raise CustomException(e,sys)
        

    def encode_data(self):
        try:
            logger.info("Encoding data")

            user_ids = self.rating_df['user_id'].unique().tolist()
            anime_ids = self.rating_df['anime_id'].unique().tolist()

            # user_ids = user_ids.astype(str)
            # anime_ids = anime_ids.astype(str)   

            self.user2user_encoded = {x:i for i,x in enumerate(user_ids)}
            self.user2user_decoded = {i:x for i,x in enumerate(user_ids)}

            self.anime2anime_encoded = {x:i for i,x in enumerate(anime_ids)}
            self.anime2anime_decoded = {i:x for i,x in enumerate(anime_ids)}    

            logger.info("Data encoded successfully")

        except Exception as e:
            logger.error("Error encoding data: %s", e)
            raise CustomException(e,sys)
        
    def train_test_split(self):
        try:
            logger.info("Splitting data into train and test")
            self.rating_df = self.rating_df.sample(frac=1,random_state=42).reset_index(drop=True)

            X = self.rating_df[["user_id", "anime_id"]].values
            y = self.rating_df["rating"].values
            test_size = 1000
            train_indices = self.rating_df.shape[0] - test_size

            X_train, X_test, y_train, y_test = X[:train_indices], X[train_indices:], y[:train_indices], y[train_indices:]
            self.X_train_array = [X_train[: , 0], X_train[: , 1]]
            self.X_test_array = [X_test[: , 0], X_test[: , 1]]   
            self.y_train = y_train
            self.y_test = y_test
            logger.info("Data split successfully")



        except Exception as e:
            logger.error("Error splitting data: %s", e)
            raise CustomException(e,sys)
    def save_artifacts(self):
        try:
            logger.info("Saving data")
            artifacts = {
                "user2user_encoded": self.user2user_encoded,
                "user2user_decoded": self.user2user_decoded,
                "anime2anime_encoded": self.anime2anime_encoded,
                "anime2anime_decoded": self.anime2anime_decoded,
            }
            for name, data in artifacts.items():
                joblib.dump(data, os.path.join(self.output_dir, f"{name}.pkl"))
                logger.info(f"Data saved successfully: {name}")
            joblib.dump(self.X_train_array, X_TRAIN_ARRAY)
            joblib.dump(self.X_test_array, X_TEST_ARRAY)
            joblib.dump(self.y_train, Y_TRAIN)
            joblib.dump(self.y_test, Y_TEST)

            self.rating_df.to_csv(RATING_DF, index=False)
            logger.info("All the Training and Testing Data saved successfully")

        except Exception as e:
            logger.error("Error saving data: %s", e)
            raise CustomException(e,sys)

    def process_anime_data(self):
        try:
            logger.info("Processing anime data")

            df = pd.read_csv(ANIME_CSV)

            cols = ["MAL_ID", "Name", "Genres", "sypnopsis"]

            synopsys_df = pd.read_csv(ANIMESYNOPSYS_CSV, usecols=cols)

            df = df.replace("Unknown", np.nan)

            def getAmineName(anime_id):
                try:
                    name = df[df.anime_id == anime_id].eng_version.values[0]
                    if name is np.nan:
                        name = df[df.anime_id == anime_id].Name.values[0]
                except:
                    print("Error")
                return name


            df["anime_id"] = df["MAL_ID"]
            df["eng_version"] = df["English name"]
            df["eng_version"] = df.anime_id.apply(lambda x:getAmineName(x))

            df.sort_values(by=["Score"],
               inplace=True,
               ascending=False,
               kind="quicksort",
               na_position="last",
               )
            df = df[["anime_id", "eng_version","Score", "Genres", "Episodes", "Type","Premiered","Members"]]

            df.to_csv(DF, index=False)

            synopsys_df.to_csv(SYNOPYS_DF, index=False)

            logger.info("Anime data processed successfully")

        except Exception as e:
            logger.error("Error processing anime data: %s", e)
            raise CustomException(e,sys)

    def run(self):
        try:
            self.load_data(usecols=["user_id", "anime_id", "rating"])
            self.filter_users(min_ratings=400)
            self.scale_ratings()
            self.encode_data()
            self.train_test_split() 
            self.save_artifacts()
            self.process_anime_data()
            logger.info("Data processing Pipeline completed successfully")
        except Exception as e:
            logger.error("Error running data processing: %s", e)
            raise CustomException(e,sys)

if __name__ == "__main__":
    data_processing = DataProcessing(input_file=ANIMELIST_CSV, output_dir=PROCESSED_DIR)
    data_processing.run()


