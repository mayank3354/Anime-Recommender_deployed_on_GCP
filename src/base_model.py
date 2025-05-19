from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Embedding, Dot, Add, Flatten, Dense, Activation,BatchNormalization
from utils.common_functions import read_yaml_file
from src.logger import get_logger
from src.custon_exception import CustomException
import sys

logger = get_logger(__name__)

class BaseModel:
    def __init__(self, config_path: str):
        try:
            self.config = read_yaml_file(config_path)
            
            logger.info("Model configuration initialized successfully")
        except Exception as e:
            logger.error("Error initializing model configuration: %s", e)
            raise CustomException(e,sys)
    def RecommenderNet(self,n_users,n_anime):
        try:
            embedding_size = self.config["model"]["embedding_size"]

            user = Input(name="user", shape=[1])

            user_embedding = Embedding(name="user_embedding", input_dim=n_users, output_dim=embedding_size)(user)

            anime = Input(name="anime", shape=[1])

            anime_embedding = Embedding(name="anime_embedding", input_dim=n_anime, output_dim=embedding_size)(anime)

            x = Dot(name="dot_product",normalize=True, axes=2)([user_embedding, anime_embedding])

            x = Flatten()(x)

            x = Dense(1, kernel_initializer="he_normal")(x)
            x = BatchNormalization()(x)
            x = Activation("sigmoid")(x)

            model = Model([user, anime], x)
            model.compile(loss=self.config['model']['loss'],
                          metrics=self.config['model']['metrics'],
                            optimizer=self.config['model']['optimizer'])

            return model
        except Exception as e:
            logger.error("Error initializing model: %s", e)
            raise CustomException(e,sys)

                    


