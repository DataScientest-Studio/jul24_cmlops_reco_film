import streamlit as st
import requests
from utils import display_movies_grid


# Charger le CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Vérification plus robuste de l'authentification
if not st.session_state.get('is_logged_in', False):
    st.warning("Veuillez vous connecter pour accéder à cette page.")
    st.switch_page("pages/4_🔐_Authentification.py")
    st.stop()


# Utilisation des headers avec le token pour l'authentification
headers = {
    "Authorization": f"Bearer {st.session_state.token}"
}

# Récupérer le token depuis la session
token = st.session_state.get('token')


st.write(f"Bienvenue 💪. Voici les 10 films que nous vous recommandons:")

try:
    response = requests.get(
        "http://fastapi:8000/",
        json={"token": token},
        headers=headers
    )
    result = response.json()
    user_id = result.get('id')
except Exception as e:
    st.error(f"Erreur de requête: {str(e)}")

# Récupérer les recommandations pour l'utilisateur
try:
    payload = {"userId": user_id}
    response = requests.post(
        "http://fastapi:8000/predict/identified_user",
        json=payload,
        headers=headers
    )

    if response.status_code == 200:
        result = response.json()
        recommendations = [result.get(i) for i in range(10)]
        display_movies_grid(recommendations)
    else:
        st.error(f"Erreur lors de la requête : {response.status_code} - {response.text}")
except ValueError as e:
    st.error("Erreur de conversion de l'ID utilisateur")
    st.stop()
except Exception as e:
    st.error(f"Erreur de requête: {str(e)}")

# Ajouter une ligne horizontale
st.markdown("---")

st.write('Nous pouvons aussi vous faire des recommandations en relation avec un film. Entrez le nom d\'un film que vous avez aimé et nous vous recommanderons des films similaires.')

# Demander à l'utilisateur de saisir le nom d'un film

movie_name = st.text_input("Entrez le nom d'un film que vous avez aimé", "Inception")

# Dans la partie recherche de films similaires
if st.button("Rechercher"):
    response = requests.post(
        "http://fastapi:8000/predict/similar_movies",
        json={"userId": st.session_state.user_id, "movie_name": movie_name},
        headers=headers
    )

    if response.status_code == 200:
        result = response.json()
        recommendations = [result.get(i) for i in range(10)]
        display_movies_grid(recommendations)
    else:
        st.error(f"Erreur lors de la requête : {response.status_code} - {response.text}")