import streamlit as st
import asyncio
from utils import get_tmdb_ids, get_movie_info_async, display_movie_info_grid
import requests

# Charger le CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.switch_page("Home.py")

user_info = st.session_state.user_info

genres = [
    "(no genres listed)",
    "Action",
    "Adventure",
    "Animation",
    "Children",
    "Comedy",
    "Crime",
    "Documentary",
    "Drama",
    "Fantasy",
    "Film-Noir",
    "Horror",
    "IMAX",
    "Musical",
    "Mystery",
    "Romance",
    "Sci-Fi",
    "Thriller",
    "War",
    "Western",
]

# Construire la user_matrix à partir des valeurs de genres
user_matrix = ",".join(str(user_info[genre]) for genre in genres)


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


st.title("Recommandations de Films basées sur votre Historique")

if user_matrix:
    api_url = "http://api_predict:8002/recommend"
    user_input = {"genres": user_matrix}

    response = requests.post(api_url, json=user_input)

    if response.status_code == 200:
        recommendations = response.json()

        if "recommendations" in recommendations and recommendations["recommendations"]:
            movie_ids = recommendations["recommendations"][0]
            asyncio.run(main(movie_ids))
        else:
            st.error("Aucune recommandation disponible.")
    else:
        st.error("Erreur lors de la récupération des recommandations.")
else:
    st.warning("Veuillez sélectionner au moins un genre.")
