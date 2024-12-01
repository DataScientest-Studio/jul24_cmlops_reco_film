import streamlit as st

def display_movies_grid(movies_info):
    # Créer deux lignes principales
    rows = [st.columns(4), st.columns(4)]
    # Diviser les films entre les deux lignes
    for idx, movie_info in movies_info.items():
        idx = int(idx)
        row_idx = idx // 4  # Déterminer la ligne (0 ou 1)
        col_idx = idx % 4   # Déterminer la colonne (0 à 3)
        with rows[row_idx][col_idx]:
            html_content = f"""
            <div class="movie-container">
                <div class="movie-tile">
                    <img src="{movie_info['poster_path']}" alt="{movie_info['title']}">
                </div>
                <div class="overlay">
                    <h5 style="color: white;">{movie_info['title']}</h5>
                    <p class="rating-badge">{round(movie_info['vote_average'], 1)} ⭐️</p>
                </div>
            </div>
            """
            st.markdown(html_content, unsafe_allow_html=True)