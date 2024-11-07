import streamlit as st
from supabase_auth import supabase, sign_out
import pandas as pd
import plotly.express as px
import numpy as np

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.switch_page("Home.py")

col1, col2, col3 = st.columns([2, 4, 1])

with col1:
    st.title("Profil Utilisateur")

with col3:
    if st.button("Se déconnecter"):
        sign_out(st.session_state.user)
        st.session_state.authenticated = False
        st.session_state.user = None
        st.rerun()

st.write(f"Email : {st.session_state.user.email}")

user_id = st.session_state.user_info["userId"]

# Création du graphique des préférences
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

# Récupérer les valeurs de genres depuis user_info
genre_values = [float(st.session_state.user_info[genre]) for genre in genres]

# Normaliser les valeurs (somme = 100%)
genre_values = np.array(genre_values)
genre_values = (genre_values / genre_values.sum()) * 100

# Créer un DataFrame pour le graphique
preferences_df = pd.DataFrame({"Genre": genres, "Préférence (%)": genre_values})

# Filtrer les genres avec une préférence > 1%
preferences_df = preferences_df[preferences_df["Préférence (%)"] > 1]

# Créer le camembert avec Plotly
fig = px.pie(
    preferences_df,
    values="Préférence (%)",
    names="Genre",
)

# Et remplacer les lignes 48-52 par :
fig.update_traces(textposition="inside", textinfo="percent+label")
fig.update_layout(
    showlegend=False,
    height=400,  # Augmentation de la hauteur
    margin=dict(t=0, b=0),  # Suppression des marges haut/bas
)

# Afficher le graphique et les notes dans deux colonnes
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Vos préférences par genre")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Récupérer les 10 dernières notes
    ratings = (
        supabase.table("ratings")
        .select("rating", "timestamp", "movies(title)", count="exact")
        .eq("userId", user_id)
        .order("timestamp", desc=True)
        .limit(10)
        .execute()
    )

    if ratings.data:
        st.subheader("Vos 10 dernières notes")

        formatted_data = []
        for rating in ratings.data:
            formatted_data.append(
                {
                    "Note": rating["rating"],
                    "Date": pd.to_datetime(rating["timestamp"], unit="s").strftime(
                        "%d/%m/%Y %H:%M"
                    ),
                    "Film": rating["movies"]["title"],
                }
            )

        df = pd.DataFrame(formatted_data)
        df = df[["Film", "Note", "Date"]]
        st.dataframe(df, hide_index=True)
    else:
        st.info("Vous n'avez pas encore noté de films.")
