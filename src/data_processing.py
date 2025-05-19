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
            self.rating_df["rating"] = self.rating_df["rating"].apply(lambda X: (X - min_rating) / (max_rating - min_rating)).astype(np.float32)

            logger.info("Ratings scaled successfully")

        except Exception as e:
            logger.error("Error scaling ratings: %s", e)
            raise CustomException(e,sys)

    def encode_data(self):
        try:
            logger.info("Encoding data")

            user_ids = self.rating_df['user_id'].unique().tolist()
            anime_ids = self.rating_df['anime_id'].unique().tolist()

            self.user2user_encoded = {x:i for i,x in enumerate(user_ids)}
            self.user2user_decoded = {i:x for i,x in enumerate(user_ids)}
            self.anime2anime_encoded = {x:i for i,x in enumerate(anime_ids)}
            self.anime2anime_decoded = {i:x for i,x in enumerate(anime_ids)}    

            logger.info("Data encoded successfully")

        except Exception as e:
            logger.error("Error encoding data: %s", e)
            raise CustomException(e,sys)

    def train_test_split(self, test_size=1000):
        try:
            logger.info("Splitting data into train and test with encoding")
            # Shuffle
            self.rating_df = self.rating_df.sample(frac=1, random_state=42).reset_index(drop=True)

            # Extract raw arrays
            raw_X = self.rating_df[["user_id", "anime_id"]].values
            y = self.rating_df["rating"].values.astype(np.float32)

            # Determine split index for holdout
            split_index = raw_X.shape[0] - test_size

            # Split raw arrays
            raw_train = raw_X[:split_index]
            raw_test  = raw_X[split_index:]
            self.y_train = y[:split_index]
            self.y_test  = y[split_index:]

            # Encode IDs using mapping dicts
            vec_user = np.vectorize(self.user2user_encoded.get)
            vec_anime = np.vectorize(self.anime2anime_encoded.get)

            train_users = vec_user(raw_train[:, 0]).astype(np.int32)
            train_animes = vec_anime(raw_train[:, 1]).astype(np.int32)
            test_users = vec_user(raw_test[:, 0]).astype(np.int32)
            test_animes = vec_anime(raw_test[:, 1]).astype(np.int32)

            # Save as list of two arrays for model.fit
            self.X_train_array = [train_users, train_animes]
            self.X_test_array  = [test_users, test_animes]

            logger.info("Data split and encoded successfully")

        except Exception as e:
            logger.error("Error splitting/encoding data: %s", e)
            raise CustomException(e,sys)

    def save_artifacts(self):
        try:
            logger.info("Saving data artifacts to %s", self.output_dir)
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
            logger.info("All training/testing data saved successfully")

        except Exception as e:
            logger.error("Error saving data: %s", e)
            raise CustomException(e,sys)

    def process_anime_data(self):
        try:
            logger.info("Processing anime metadata and synopsis")

            df = pd.read_csv(ANIME_CSV)
            synopsys_df = pd.read_csv(ANIMESYNOPSYS_CSV, usecols=["MAL_ID", "Name", "Genres", "sypnopsis"])

            df = df.replace("Unknown", np.nan)

            def getAnimeName(anime_id):
                try:
                    row = df[df.MAL_ID == anime_id]
                    if not row.empty and not pd.isna(row.eng_version.values[0]):
                        return row.eng_version.values[0]
                    elif not row.empty:
                        return row.Name.values[0]
                except Exception:
                    pass
                return None

            df["anime_id"] = df["MAL_ID"]
            df["eng_version"] = df["anime_id"].apply(getAnimeName)

            df.sort_values(by="Score", ascending=False, na_position="last", inplace=True)
            df = df[["anime_id", "eng_version", "Score", "Genres", "Episodes", "Type", "Premiered", "Members"]]

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
            self.train_test_split(test_size=1000)
            self.save_artifacts()
            self.process_anime_data()
            logger.info("Data processing pipeline completed successfully")
        except Exception as e:
            logger.error("Error running data processing: %s", e)
            raise CustomException(e,sys)

if __name__ == "__main__":
    data_processing = DataProcessing(input_file=ANIMELIST_CSV, output_dir=PROCESSED_DIR)
    data_processing.run()
