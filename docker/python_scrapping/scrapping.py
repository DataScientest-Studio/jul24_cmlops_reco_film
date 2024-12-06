import os
import time
import logging
import requests
from bs4 import BeautifulSoup as bs
from sqlalchemy import create_engine, table, column, select, insert

# Configurer le logger pour suivre les événements et les erreurs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Définition des tables SQLAlchemy pour les opérations d'upsert
table_movies = table('movies',
    column('movieid'),
    column('title'),
    column('genres'),
    column('year')
)

table_links = table('links',
    column('id'),
    column('movieid'),
    column('imdbid'),
    column('tmdbid')
)

tmdb_token = os.getenv("TMDB_TOKEN")

def load_config():
    """Charge la configuration de la base de données à partir des variables d'environnement."""
    config = {
        'host': os.getenv('AIRFLOW_POSTGRESQL_SERVICE_HOST'),
        'database': os.getenv('DATABASE'),
        'user': os.getenv('USER'),
        'password': os.getenv('PASSWORD')
    }
    return config

def scrape_imdb_first_page():
    """Scrape les données des films depuis IMDb et les renvoie sous forme de listes."""
    start_time = time.time()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # Récupérer la page des box-offices d'IMDb
        page = requests.get("https://www.imdb.com/chart/boxoffice", headers=headers)
        page.raise_for_status()  # Vérifier que la requête a réussi
        soup = bs(page.content, 'lxml')  # Extraire les liens et titres des films

        links = [a['href'] for a in soup.find_all('a', class_='ipc-title-link-wrapper')]
        cleaned_links = [link.split('/')[2].split('?')[0].replace('tt', '') for link in links]

        logger.info("Liens IMDB nettoyés: %s", cleaned_links)
        return cleaned_links

    except requests.RequestException as e:
        logger.error(f"Erreur lors de la récupération de la page IMDb: {e}")

    finally:
        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"Durée du scraping IMDb: {duration} secondes")

def genres_request():
    """Effectue des requêtes à l'API TMDB pour récupérer les informations des films."""
    url = "https://api.themoviedb.org/3/genre/movie/list?language=en"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {tmdb_token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        genres = {str(genre["id"]): genre["name"] for genre in data["genres"]}
        return genres
        logger.info("Genres récupérés avec succès: %s", genres)

def api_tmdb_request():
    """Effectue des requêtes à l'API TMDB pour récupérer les informations des films."""
    results = {}
    cleaned_links = scrape_imdb_first_page()
    genres = genres_request()
    logger.info("Liens nettoyés reçus via XCom: %s", cleaned_links)

    for index, movie_id in enumerate(cleaned_links):
        url = f"https://api.themoviedb.org/3/find/tt{movie_id}?external_source=imdb_id"

        logger.info("Url pour le film index %s: %s", index, url)

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {tmdb_token}"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            logger.info("Données reçues pour le film index %s: %s", index, data)

            if data["movie_results"]:
                movie_info = data["movie_results"][0]
                release_date = movie_info["release_date"]
                release_year = release_date.split("-")[0]  # Extraire l'année

                results[str(index)] = {
                    "tmdb_id": movie_info["id"],
                    "title": movie_info["title"],
                    "genre_ids": movie_info['genre_ids'],
                    "imbd_id": movie_id,
                    "date": release_date,
                    "year": release_year,
                    "genres": [genres[str(genre_id)] for genre_id in movie_info['genre_ids']]
                }
            else:
                results[str(index)] = {"error": f"Request failed with status code {response.status_code}"}

        return results

def insert_data_movies():
    """Insère les données des films dans la base de données en utilisant SQLAlchemy."""
    start_time = time.time()
    api_results = api_tmdb_request()

    config = load_config()  # Charger la configuration de la base de données
    conn_string = f"postgresql://{config['user']}:{config['password']}@{config['host']}/{config['database']}"

    try:
        db = create_engine(conn_string)
        with db.begin() as conn:
            for index, movie_data in api_results.items():
                # Vérifier si une erreur a été retournée pour ce film
                if "error" in movie_data:
                    logger.error(f"Erreur pour le film index {index}: {movie_data['error']}")
                    continue

                title = movie_data["title"]
                genres = movie_data["genres"]
                imdb_id = movie_data["imbd_id"]
                tmdb_id = movie_data["tmdb_id"]
                year = movie_data["year"]

                # Éviter les doublons dans la base de données
                query = select([table_movies]).where(
                    (table_movies.c.title == title) & (table_movies.c.year == year)
                )

                result = conn.execute(query).fetchone()

                if result is None:  # Si le film n'existe pas déjà
                    genres_str = ','.join(genres)  # Convertir la liste de genres en chaîne de caractères

                    # Insertion du film
                    insert_query = insert(table_movies).values(
                        movieid=None,  # Laissez PostgreSQL gérer l'ID si c'est une séquence
                        title=title,
                        genres=genres_str,
                        year=year
                    )
                    conn.execute(insert_query)

                    # Insertion du lien avec l'ID du film
                    last_inserted_id_query = select([table_movies.c.movieid]).where(
                        (table_movies.c.title == title) & (table_movies.c.year == year)
                    )
                    last_inserted_id = conn.execute(last_inserted_id_query).fetchone()[0]

                    insert_link_query = insert(table_links).values(
                        id=None,  # Laissez PostgreSQL gérer l'ID si c'est une séquence
                        movieid=last_inserted_id,
                        imdbid=imdb_id,
                        tmdbid=tmdb_id
                    )
                    conn.execute(insert_link_query)

                    logger.info(f"Film inséré: {title} avec ID {last_inserted_id}")
                else:
                    logger.info(f"Le film {title} existe déjà dans la base de données.")

            logger.info("Données insérées avec succès dans les tables movies & links.")

    except Exception as e:
        logger.error(f"Erreur lors de l'insertion des données: {e}")

    finally:
        end_time = time.time()
        duration = end_time - start_time

        logger.info(f"Durée de l'insertion des données: {duration} secondes")

if __name__ == "__main__":
    insert_data_movies()