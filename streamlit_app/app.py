import streamlit as st
import requests


st.title("Movie Recommendation System")

genres = [
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

# Select some genres
selected_genres = st.multiselect("Select your favorite genres", genres)

# Générer une chaîne de caractères avec des 1 pour les genres sélectionnés et des 0 pour les autres
genre_string = "".join(["1" if genre in selected_genres else "0" for genre in genres])

# Ajouter 0 au début de la chaîne
genre_string = "0" + genre_string

if st.button("Show genre string"):
    st.write("String des genres sélectionnés :")
    st.write(genre_string)

if st.button("Obtenir des recommandations"):
    if genre_string:
        # Envoi de la requête POST à l'API FastAPI
        api_url = "http://api_predict:8000/recommend"
        user_input = {"genres": genre_string}

        response = requests.post(api_url, json=user_input)

        # Gestion de la réponse de l'API
        if response.status_code == 200:
            recommendations = response.json()
            st.write("Voici vos recommandations de films :")
            st.write(recommendations)
        else:
            st.error(
                "Erreur lors de la récupération des recommandations. Veuillez réessayer."
            )
    else:
        st.warning("Veuillez remplir tous les champs.")

st.write("Powered by FastAPI and Streamlit")
