from utils.helpers import *

from config.paths_config import *

#print(getAnimeFrame(40028,DF))

#print(getSynopsis(40028,SYNOPYS_DF))

#print(find_similar_animes("Naruto",ANIME_WEIGHTS_PATH,ANIME2ANIME_ENCODED,ANIME2ANIME_DECODED,DF))

similar_users = find_similar_users(11880,USER_WEIGHTS_PATH,USER2USER_ENCODED,USER2USER_DECODED)

user_pref = get_user_preferences(11880,RATING_DF,DF)

user_recomm = get_user_recommendations(similar_users,user_pref,DF,SYNOPYS_DF,RATING_DF)

print(user_recomm)
