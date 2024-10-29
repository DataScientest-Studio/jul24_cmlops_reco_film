import os
import aiohttp
import streamlit as st


async def get_tmdb_ids(movie_ids):
    api_url = "http://api_data:8001/get_tmdb_ids"
    async with aiohttp.ClientSession() as session:
        async with session.post(api_url, json=movie_ids) as response:
            if response.status == 200:
                return await response.json()
            else:
                st.error(f"Erreur lors de la récupération des tmdbIds")
                return {}


async def get_movie_info_async(movie_id, tmdb_id):
    api_url_tmdb = f"https://api.themoviedb.org/3/movie/{tmdb_id}?language=fr-FR"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {os.environ['TMDB_API_TOKEN']}",
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url_tmdb, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    "title": data["title"],
                    "year": data["release_date"][:4],
                    "average_rating": round(data["vote_average"], 1),
                    "genres": [genre["name"] for genre in data["genres"]],
                    "cover_url": f"https://image.tmdb.org/t/p/w500{data['poster_path']}",
                }
            else:
                st.error(
                    f"Erreur lors de la récupération des informations pour le film ID {movie_id}"
                )
                return None


async def display_movie_info_grid(movies_info):
    cols = st.columns(6)
    for idx, movie_info in enumerate(movies_info):
        with cols[idx % 6]:  # Utiliser toutes les colonnes de 0 à 3
            html_content = f"""
            <div class="movie-container">
                <div class="movie-tile">
                    <img src="{movie_info['cover_url']}" alt="{movie_info['title']}">
                </div>
                <div class="overlay">
                    <h4 style="color: white;">{movie_info['title']}</h4>
                    <p>{movie_info['year']}</p>
                    <p class="rating-badge">{movie_info['average_rating']} ⭐️</p>
                    <div style="display: flex; flex-wrap: wrap;">
            """
            for genre in movie_info["genres"]:
                html_content += f'<span class="genre-badge">{genre}</span>'
            html_content += """
                    </div>
                </div>
            </div>
            """
            st.markdown(html_content, unsafe_allow_html=True)
