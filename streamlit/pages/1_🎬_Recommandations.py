import streamlit as st
from utils import display_movies_grid
import requests
from supabase_auth import supabase

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

st.title("Recommandations de Films basées sur votre Historique")

if user_matrix:
    api_url = "http://api-predict:8000/recommend"
    user_input = {"genres": user_matrix}

    response = requests.post(api_url, json=user_input)

    if response.status_code == 200:
        recommendations = response.json()

        if "recommendations" in recommendations and recommendations["recommendations"]:
            movie_ids = recommendations["recommendations"][0]
            movies_info = (
                supabase.table("movies").select("*").in_("movieId", movie_ids).execute()
            )
            display_movies_grid(movies_info.data)
        else:
            st.error("Aucune recommandation disponible.")
    else:
        st.error("Erreur lors de la récupération des recommandations.")
else:
    st.warning("Veuillez sélectionner au moins un genre.")

if st.button("Afficher les infos du modèle"):
    model_info_url = "http://api-predict:8000/model_info"
    model_info = requests.get(model_info_url)
    st.write(f"Model info: {model_info.json()}")

# if st.button("Recharger le modèle"):
#     reload_model_url = "http://api-predict:8000/reload_model"
#     reload_model = requests.post(reload_model_url)
#     if reload_model.status_code == 200:
#         st.success("Modèle rechargé avec succès")
#     else:
#         st.error(f"Erreur lors du rechargement du modèle: {reload_model.json()}")
