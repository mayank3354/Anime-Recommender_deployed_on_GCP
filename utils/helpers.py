import pandas as pd
import numpy as np
import joblib
from config.paths_config import *

###### GET ANIME FRAME

def getAnimeFrame(anime,path_df):
    try:
        df = pd.read_csv(path_df)
        if isinstance(anime,int):
            return df[df["anime_id"] == anime]
        elif isinstance(anime,str):
            return df[df["eng_version"] == anime]
        else:
            raise ValueError("Invalid input")
    except Exception as e:
        raise e
        
######### GET SYNOPYS #########


def getSynopsis(anime_id,path_synopsys_df):
    try:
        synopsys_df = pd.read_csv(path_synopsys_df)
        if isinstance(anime_id,int):
            return synopsys_df[synopsys_df["MAL_ID"] == anime_id].sypnopsis.values[0]
        elif isinstance(anime_id,str):
            return synopsys_df[synopsys_df["Name"] == anime_id].sypnopsis.values[0]
        else:
            raise ValueError("Invalid input")
    except:
        print("Error")
        return None
        

########## CONTENT BASED RECOMMENDATION #########
########## find similar anime #########

def find_similar_animes(name, path_anime_weights, path_anime2anime_encoded,
                        path_anime2anime_decoded, path_df,
                        n=10, return_dist=False,
                        neg=False):
    try:
        df = pd.read_csv(path_df)
        anime2anime_encoded = joblib.load(path_anime2anime_encoded)
        anime2anime_decoded = joblib.load(path_anime2anime_decoded)
        anime_weights = joblib.load(path_anime_weights)

        index = getAnimeFrame(name, df).anime_id.values[0]
        encoded_index = anime2anime_encoded.get(index)

        if encoded_index is None:
            raise ValueError(f"Anime ID {index} not found in encoding.")

        dists = np.dot(anime_weights, anime_weights[encoded_index])
        sorted_dists = np.argsort(dists)

        n = n + 1

        if neg:
            closest = sorted_dists[:n]
        else:
            closest = sorted_dists[-n:][::-1]

        print(f"Anime closest to {name}")

        if return_dist:
            return dists, closest

        similarityArr = []
        for close in closest:
            decoded_id = anime2anime_decoded.get(close)
            if decoded_id is None:
                continue

            synopsis = getSynopsis(decoded_id)
            anime_frame = getAnimeFrame(decoded_id, df)

            if anime_frame.empty:
                continue

            anime_name = anime_frame.eng_version.values[0]
            genre = anime_frame.Genres.values[0]
            similarity = dists[close]

            similarityArr.append({
                "anime_id": decoded_id,
                "name": anime_name,
                "similarity": similarity,
                "genre": genre,
                "synopsis": synopsis
            })

        Frame = pd.DataFrame(similarityArr).sort_values(by="similarity", ascending=False)

        return Frame[Frame.anime_id != index].drop("anime_id", axis=1)

    except Exception as e:
        print(f"Error Occurred: {e}")


########## 4. FIND SIMILAR USERS     #########

def find_similar_users(item_input, path_user_weights, path_user2user_encoded, path_user2user_decoded, 
                       n=10, return_dist=False, neg=False):
    try:
        
        user2user_encoded = joblib.load(path_user2user_encoded)
        user2user_decoded = joblib.load(path_user2user_decoded)
        user_weights = joblib.load(path_user_weights)
        
        index = item_input
        encoded_index = user2user_encoded.get(item_input)

        if encoded_index is None:
            raise ValueError(f"User ID {index} not found in encoded dictionary.")

        weights = user_weights
        dists = np.dot(weights, weights[encoded_index])
        sorted_dists = np.argsort(dists)

        n = n + 1  # include self

        if neg:
            closest = sorted_dists[:n]
        else:
            closest = sorted_dists[-n:][::-1]

        if return_dist:
            return dists, closest

        similarityArr = []
        for close in closest:
            similarity = dists[close]
            decoded_id = user2user_decoded.get(close)

            if decoded_id is None:
                print(f"Warning: user2user_decoded missing index {close}")
                continue

            if decoded_id != index:
                similarityArr.append({
                    "similar_users": decoded_id,
                    "similarity": similarity
                })

        if not similarityArr:
            raise ValueError("No similar users found — similarityArr is empty.")

        similar_users = pd.DataFrame(similarityArr).sort_values(by="similarity", ascending=False)
        return similar_users

    except Exception as e:
        print(f"Error Occurred: {e}")



########## 5. GET USER PREFERENCES #########

def get_user_preferences(user_id, path_rating_df, path_df, verbose=0, plot=False):
    rating_df = pd.read_csv(path_rating_df)
    df = pd.read_csv(path_df)
    animes_watched_by_user = rating_df[rating_df["user_id"] == user_id]
    user_rating_percentile = np.percentile(animes_watched_by_user["rating"], 75)

    animes_watched_by_user = animes_watched_by_user[animes_watched_by_user["rating"] >= user_rating_percentile]

    top_animes_by_user = (
        animes_watched_by_user.sort_values(by="rating", ascending=False)
        .anime_id.values
    )

    anime_df_rows = df[df["anime_id"].isin(top_animes_by_user)]
    anime_df_rows = anime_df_rows[["eng_version", "Genres"]]

    # if plot:
    #     fav_genres = getFavGenre(anime_df_rows, plot=plot)


    # if verbose:
    #     print(f"User {user_id} has watched {len(animes_watched_by_user)} animes with rating greater than {user_rating_percentile}")

    return anime_df_rows

######### 6. USER BASED RECOMMENDATION #########


def get_user_recommendations(similar_users, user_pref, path_df, path_synopsys_df, path_rating_df,n=10):
    df = pd.read_csv(path_df)
    synopsys_df = pd.read_csv(path_synopsys_df)
    rating_df = pd.read_csv(path_rating_df)

    recommended_animes = []
    anime_list = []

    for user_id in similar_users["similar_users"].values:
        pref_list = get_user_preferences(int(user_id), rating_df, df)

        pref_list = pref_list[~pref_list.eng_version.isin(user_pref.eng_version.values)]

        if not pref_list.empty:
            anime_list.append(pref_list.eng_version.values)

    if anime_list:
        anime_list = pd.DataFrame(anime_list)

        sorted_list = pd.DataFrame(pd.Series(anime_list.values.ravel()).value_counts()).head(n)

        for i, anime_name in enumerate(sorted_list.index):
            n_user_pref = sorted_list[sorted_list.index == anime_name].values[0][0]

            if isinstance(anime_name, str):
                frame = getAnimeFrame(anime_name, df)

                anime_id = frame.anime_id.values[0]
                genre =frame.Genres.values[0]
                synopsis = getSynopsis(int(anime_id))

                recommended_animes.append({
                    "n": n_user_pref,
                    "anime_name": anime_name,
                    "genre": genre,
                    "synopsis": synopsis
                })

    return pd.DataFrame(recommended_animes).head(n)











