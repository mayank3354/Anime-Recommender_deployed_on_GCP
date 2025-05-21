import pandas as pd
import numpy as np
import joblib
from config.paths_config import *
from fuzzywuzzy import process
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

# def find_similar_animes(name, path_anime_weights, path_anime2anime_encoded,
#                         path_anime2anime_decoded, path_anime_df,path_synopsys_df,
#                         n=10, return_dist=False,
#                         neg=False):
#     try:
#         # df = pd.read_csv(path_anime_df)
#         anime2anime_encoded = joblib.load(path_anime2anime_encoded)
#         anime2anime_decoded = joblib.load(path_anime2anime_decoded)
#         anime_weights = joblib.load(path_anime_weights)

#         index = getAnimeFrame(name, path_anime_df).anime_id.values[0]
#         encoded_index = anime2anime_encoded.get(index)

#         if encoded_index is None:
#             raise ValueError(f"Anime ID {index} not found in encoding.")

#         dists = np.dot(anime_weights, anime_weights[encoded_index])
#         sorted_dists = np.argsort(dists)

#         n = n + 1

#         if neg:
#             closest = sorted_dists[:n]
#         else:
#             closest = sorted_dists[-n:][::-1]

#         print(f"Anime closest to {name}")

#         if return_dist:
#             return dists, closest

#         similarityArr = []
#         for close in closest:
#             decoded_id = anime2anime_decoded.get(close)
#             if decoded_id is None:
#                 continue

#             synopsis = getSynopsis(decoded_id,path_synopsys_df)
#             anime_frame = getAnimeFrame(decoded_id, path_anime_df)

#             if anime_frame.empty:
#                 continue

#             anime_name = anime_frame.eng_version.values[0]
#             genre = anime_frame.Genres.values[0]
#             similarity = dists[close]

#             similarityArr.append({
#                 "anime_id": decoded_id,
#                 "name": anime_name,
#                 "similarity": similarity,
#                 "genre": genre,
#                 "synopsis": synopsis
#             })

#         Frame = pd.DataFrame(similarityArr).sort_values(by="similarity", ascending=False)

#         return Frame[Frame.anime_id != index].drop("anime_id", axis=1)

#     except Exception as e:
#         print(f"Error Occurred: {e}")

def find_similar_animes(
    name,
    path_anime_weights,
    path_anime2anime_encoded,
    path_anime2anime_decoded,
    path_anime_df,
    path_synopsys_df,
    n=10,
    return_dist=False,
    neg=False,
    fuzzy_threshold=70,
    genre_filter=None
):
    """
    Find top-n similar animes to the given name, using precomputed embeddings.

    Parameters:
      - name: anime title (string) or anime_id (int)
      - path_anime_weights: path to user embedding .pkl
      - path_anime2anime_encoded: path to rawID->index map .pkl
      - path_anime2anime_decoded: path to index->rawID map .pkl
      - path_anime_df: cleaned anime metadata csv path
      - path_synopsys_df: anime synopsis csv path
      - n: number of recommendations
      - return_dist: if True, return raw distance array & indices
      - neg: if True, return least similar instead of most
      - fuzzy_threshold: min score for fuzzy-match on title
      - genre_filter: list of genres to include in results

    Returns:
      DataFrame of recommendations with columns:
        ['name', 'genre', 'similarity', 'synopsis']
    """
    # cache loads
    if not hasattr(find_similar_animes, "_cache"):
        find_similar_animes._cache = {}

    cache = find_similar_animes._cache

    # load once
    if 'anime2anime_encoded' not in cache:
        cache['anime2anime_encoded'] = joblib.load(path_anime2anime_encoded)
        cache['anime2anime_decoded'] = joblib.load(path_anime2anime_decoded)
        cache['anime_weights']       = joblib.load(path_anime_weights)
        cache['anime_df']            = pd.read_csv(path_anime_df)
        cache['sync_df']             = pd.read_csv(path_synopsys_df)

    anime2anime_encoded = cache['anime2anime_encoded']
    anime2anime_decoded = cache['anime2anime_decoded']
    anime_weights       = cache['anime_weights']
    anime_df            = cache['anime_df']
    sync_df             = cache['sync_df']

    # resolve name to ID
    if isinstance(name, str):
        # fuzzy match on eng_version
        candidates = anime_df['eng_version'].dropna().unique()
        match, score = process.extractOne(name, candidates)
        if score < fuzzy_threshold:
            raise ValueError(f"No close match for '{name}' (best '{match}' at {score})")
        idx = anime_df[anime_df['eng_version'] == match].anime_id.values[0]
    elif isinstance(name, int):
        idx = name
    else:
        raise ValueError("Name must be int anime_id or string title.")

    encoded_index = anime2anime_encoded.get(idx)
    if encoded_index is None:
        raise KeyError(f"Anime ID {idx} not in encoded map.")

    # compute similarity
    dists = np.dot(anime_weights, anime_weights[encoded_index])
    ordered = np.argsort(dists)
    if neg:
        candidates = ordered[:n+1]
    else:
        candidates = ordered[-(n+1):][::-1]

    # build results
    records = []
    for j in candidates:
        raw_id = anime2anime_decoded.get(j)
        if raw_id == idx:
            continue
        meta = anime_df[anime_df.anime_id == raw_id]
        if meta.empty:
            continue
        title = meta.eng_version.values[0]
        genres = meta.Genres.values[0]
        if genre_filter:
            # include only if any genre in filter
            if not any(g.strip() in genres.split(',') for g in genre_filter):
                continue
        sim_score = float(dists[j])
        synopsis = None
        row = sync_df[sync_df.MAL_ID == raw_id]
        if not row.empty:
            synopsis = row.sypnopsis.values[0]

        records.append({
            'name': title,
            'genre': genres,
            'similarity': sim_score,
            'synopsis': synopsis
        })
        if len(records) >= n:
            break

    result_df = pd.DataFrame(records)
    if return_dist:
        return dists, candidates
    return result_df


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


def get_user_recommendations(similar_users, user_pref, path_anime_df, path_synopsys_df, path_rating_df,n=10):
    # df = pd.read_csv(path_anime_df)
    # synopsys_df = pd.read_csv(path_synopsys_df)
    # rating_df = pd.read_csv(path_rating_df)

    recommended_animes = []
    anime_list = []

    for user_id in similar_users["similar_users"].values:
        pref_list = get_user_preferences(int(user_id), path_rating_df, path_anime_df)

        pref_list = pref_list[~pref_list.eng_version.isin(user_pref.eng_version.values)]

        if not pref_list.empty:
            anime_list.append(pref_list.eng_version.values)

    if anime_list:
        anime_list = pd.DataFrame(anime_list)

        sorted_list = pd.DataFrame(pd.Series(anime_list.values.ravel()).value_counts()).head(n)

        for i, anime_name in enumerate(sorted_list.index):
            n_user_pref = sorted_list[sorted_list.index == anime_name].values[0][0]

            if isinstance(anime_name, str):
                frame = getAnimeFrame(anime_name, path_anime_df)

                anime_id = frame.anime_id.values[0]
                genre =frame.Genres.values[0]
                synopsis = getSynopsis(int(anime_id),path_synopsys_df)

                recommended_animes.append({
                    "n": n_user_pref,
                    "anime_name": anime_name,
                    "genre": genre,
                    "synopsis": synopsis
                })

    return pd.DataFrame(recommended_animes).head(n)











