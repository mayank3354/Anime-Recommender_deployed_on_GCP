from utils.helpers import *

from config.paths_config import *

# print(getAnimeFrame(459,DF))

# print(getSynopsis(459,SYNOPYS_DF))

# print(find_similar_animes("Naruto",ANIME_WEIGHTS_PATH,ANIME2ANIME_ENCODED,ANIME2ANIME_DECODED,DF,SYNOPYS_DF))

# similar_users = find_similar_users(459,USER_WEIGHTS_PATH,USER2USER_ENCODED,USER2USER_DECODED)
# print(similar_users)
# user_pref = get_user_preferences(459,RATING_DF,DF)
# print(user_pref)
# user_recomm = get_user_recommendations(similar_users,user_pref,DF,SYNOPYS_DF,RATING_DF)

# print(user_recomm)


from pipeline.prediction_pipeline import hybrid_recommendation

print(hybrid_recommendation(459))
