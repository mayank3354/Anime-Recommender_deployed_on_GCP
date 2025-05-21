from config.paths_config import *
from utils.helpers import *


def hybrid_recommendation(
    user_id,
    cf_weight: float = 0.5,     # collaborative‐filtering blend‐weight
    cb_weight: float = 0.5      # content‐based blend‐weight
):
    # inside, use the GLOBAL embedding matrices:
    # user_weights  ← your 2D numpy array of user embeddings
    # anime_weights ← your 2D numpy array of anime embeddings

    # 1) Collaborative filtering:
    similar_users = find_similar_users(
        user_id,
        USER_WEIGHTS_PATH,             # ← the matrix!
        USER2USER_ENCODED,
        USER2USER_DECODED,
        n=10
    )
    if similar_users is None or similar_users.empty:
        print("No similar users found. Returning empty recommendation.")
        return []

    # 2) This user’s own preferences:
    user_pref = get_user_preferences(user_id, RATING_DF, DF)

    # 3) User‐based recommendations:
    user_recs = get_user_recommendations(
        similar_users,
        user_pref,
        DF,
        SYNOPYS_DF,
        RATING_DF,
        n=10
    )
    if user_recs is None or user_recs.empty:
        print("No user-based recommendations found.")
        return []

    user_list = user_recs["anime_name"].tolist()

    # 4) Content‐based recommendations on those:
    content_list = []
    for anime in user_list:
        sim_animes = find_similar_animes(
            anime,
            ANIME_WEIGHTS_PATH,          # ← the matrix!
            ANIME2ANIME_ENCODED,
            ANIME2ANIME_DECODED,
            DF,
            SYNOPYS_DF,
            n=10
        )
        if sim_animes is not None and not sim_animes.empty:
            content_list.extend(sim_animes["name"].tolist())

    # 5) Combine scores using the *floats* cf_weight & cb_weight
    combined = {}
    for a in user_list:
        combined[a] = combined.get(a, 0) + cf_weight
    for a in content_list:
        combined[a] = combined.get(a, 0) + cb_weight

    # 6) Top‐10
    sorted_items = sorted(combined.items(), key=lambda x: x[1], reverse=True)
    return [anime for anime, _ in sorted_items[:10]]
