import streamlit as st
import asyncio
from utils import get_tmdb_ids, get_movie_info_async, display_movie_info_grid
import requests

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Veuillez vous connecter pour accéder à cette page.")
    st.stop()

# Charger le CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


async def main(movie_ids):
    tmdb_ids = await get_tmdb_ids(movie_ids)
    info_tasks = [
        get_movie_info_async(movie_id, tmdb_ids.get(str(movie_id)))
        for movie_id in movie_ids
        if tmdb_ids.get(str(movie_id))
    ]
    movies_info = await asyncio.gather(*info_tasks)
    movies_info = [movie_info for movie_info in movies_info if movie_info is not None]
    await display_movie_info_grid(movies_info)


# TODO remove this when Auth is implemented
# user_matrix = "0.0,0.37714285714285717,0.41714285714285715,0.05714285714285714,0.10857142857142857,0.2342857142857143,0.12,0.0,0.24571428571428572,0.3942857142857143,0.0,0.2571428571428571,0.011428571428571429,0.017142857142857144,0.10285714285714286,0.06285714285714286,0.22857142857142856,0.24,0.05142857142857143,0.022857142857142857"
# user_matrix = "0.0,0.3114754098360656,0.2786885245901639,0.01639344262295082,0.01639344262295082,0.16393442622950818,0.01639344262295082,0.0,0.3114754098360656,0.01639344262295082,0.01639344262295082,0.29508196721311475,0.01639344262295082,0.03278688524590164,0.06557377049180328,0.09836065573770492,0.3770491803278688,0.3114754098360656,0.06557377049180328,0.03278688524590164"
# user_matrix = "0.0,0.32620320855614976,0.26737967914438504,0.0213903743315508,0.053475935828877004,0.27807486631016043,0.11229946524064172,0.0053475935828877,0.31016042780748665,0.10695187165775401,0.0053475935828877,0.1711229946524064,0.0,0.03208556149732621,0.058823529411764705,0.0855614973262032,0.49732620320855614,0.26737967914438504,0.03208556149732621,0.016042780748663103"
# user_matrix = "0.0,0.4642857142857143,0.21428571428571427,0.07142857142857142,0.14285714285714285,0.39285714285714285,0.21428571428571427,0.0,0.2857142857142857,0.10714285714285714,0.0,0.0,0.0,0.07142857142857142,0.10714285714285714,0.14285714285714285,0.17857142857142858,0.4642857142857143,0.03571428571428571,0.03571428571428571"
user_matrix = "0.0,0.2727272727272727,0.3181818181818182,0.09090909090909091,0.16666666666666666,0.36363636363636365,0.10606060606060606,0.0,0.4090909090909091,0.16666666666666666,0.0,0.015151515151515152,0.045454545454545456,0.12121212121212122,0.030303030303030304,0.24242424242424243,0.15151515151515152,0.22727272727272727,0.015151515151515152,0.030303030303030304"
# user_matrix = "0.0,0.07692307692307693,0.0,0.0,0.0,0.38461538461538464,0.15384615384615385,0.038461538461538464,0.4230769230769231,0.038461538461538464,0.0,0.11538461538461539,0.0,0.0,0.0,0.11538461538461539,0.15384615384615385,0.38461538461538464,0.07692307692307693,0.038461538461538464"

st.title("Recommandations de Films")

with st.expander("Afficher la matrice utilisateur"):
    st.write(user_matrix)

if st.button("Obtenir des recommandations"):
    if user_matrix:
        api_url = "http://api_predict:8002/recommend"
        user_input = {"genres": user_matrix}

        response = requests.post(api_url, json=user_input)

        if response.status_code == 200:
            recommendations = response.json()
            st.write("Voici vos recommandations de films :")

            if (
                "recommendations" in recommendations
                and recommendations["recommendations"]
            ):
                movie_ids = recommendations["recommendations"][0]
                asyncio.run(main(movie_ids))
            else:
                st.error("Aucune recommandation disponible.")
        else:
            st.error("Erreur lors de la récupération des recommandations.")
    else:
        st.warning("Veuillez sélectionner au moins un genre.")
