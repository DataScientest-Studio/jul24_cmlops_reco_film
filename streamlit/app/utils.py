import streamlit as st

def display_movies_grid(movies_info):
    cols = st.columns(6)
    for idx, movie_info in enumerate(movies_info):
        with cols[idx % 6]:
            html_content = f"""
            <div class="movie-container">
                <div class="movie-tile">
                    <img src="{movie_info['cover_link']}" alt="{movie_info['original_title']}">
                </div>
                <div class="overlay">
                    <h5 style="color: white;">{movie_info['original_title']}</h5>
                    <p>{movie_info['year']}</p>
                    <p class="rating-badge">{round(movie_info['vote_average'], 1)} ⭐️</p>
                </div>
            </div>
            """
            st.markdown(html_content, unsafe_allow_html=True)