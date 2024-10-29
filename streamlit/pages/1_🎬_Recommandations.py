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
user_matrix = "0.0,0.07692307692307693,0.0,0.0,0.0,0.38461538461538464,0.15384615384615385,0.038461538461538464,0.4230769230769231,0.038461538461538464,0.0,0.11538461538461539,0.0,0.0,0.0,0.11538461538461539,0.15384615384615385,0.38461538461538464,0.07692307692307693,0.038461538461538464"

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
