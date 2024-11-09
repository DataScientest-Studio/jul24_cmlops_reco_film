import streamlit as st


def display_movies_grid(movies_info):
    cols = st.columns(6)
    for idx, movie_info in enumerate(movies_info):
        with cols[idx % 6]:
            genres = movie_info["genres"].split("|")

            html_content = f"""
            <div class="movie-container">
                <div class="movie-tile">
                    <img src="{movie_info['posterUrl']}" alt="{movie_info['title']}">
                </div>
                <div class="overlay">
                    <h5 style="color: white;">{movie_info['title']}</h5>
                    <p>{movie_info['year']}</p>
                    <p class="rating-badge">{round(movie_info['rating'], 1)} ⭐️</p>
                    <div style="display: flex; flex-wrap: wrap;">
            """
            for genre in genres:
                html_content += f'<span class="genre-badge">{genre}</span>'
            html_content += """
                    </div>
                </div>
            </div>
            """
            st.markdown(html_content, unsafe_allow_html=True)
