from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import re
import os
from dotenv import load_dotenv
import psycopg2
from contextlib import contextmanager
import logging
from airflow.utils.dates import days_ago
from airflow.hooks.base_hook import BaseHook
import time
from airflow.exceptions import AirflowNotFoundException
from sqlalchemy import create_engine, table, column
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime

# Configurer le logger pour suivre les événements et les erreurs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Définition des tables SQLAlchemy pour les opérations d'upsert
table_movies = table('movies',
    column('movieId'),
    column('title'),
    column('genres'),
    column('year')
)

table_ratings = table('ratings',
    column('id'),
    column('userId'),
    column('movieId'),
    column('rating'),
    column('timestamp'),
    column('bayesian_mean')
)

table_links = table('links',
    column('id'),
    column('movieId'),
    column('imdbId'),
    column('tmdbId')
)

table_users = table('users',
    column('userId'),
    column('username'),
    column('email'),
    column('hached_password')
)

def load_config():
    """Charge la configuration de la base de données à partir des variables d'environnement."""
    config = {}
    config['host'] = os.getenv('AIRFLOW_POSTGRESQL_SERVICE_HOST')
    config['database'] = os.getenv('DATABASE')
    config['user'] = os.getenv('USER')
    config['password'] = os.getenv('PASSWORD')
    return config

def connect(config):
    """Connecte au serveur PostgreSQL."""
    try:
        with psycopg2.connect(**config) as conn:
            print('Connected to the PostgreSQL server.')
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)

def execute_query_psql(query, config):
    """Exécute une requête SQL pour insérer des données dans une table."""
    conn_string = 'postgresql://' + config['user'] + ':' + config['password'] + '@' + config['host'] + '/' + config['database']
    try:
        db = create_engine(conn_string)
        with db.begin() as conn:
            res = conn.execute(query)
            return res.rowcount  # Retourne le nombre de lignes affectées par la requête
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def scrape_imdb_first_page(task_instance):
    """Scrape les données des films depuis IMDb et les renvoie sous forme de listes."""
    start_time = time.time()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # Récupérer la page des box-offices d'IMDb
        page = requests.get("https://www.imdb.com/chart/boxoffice", headers=headers)
        page.raise_for_status()  # Vérifier que la requête a réussi

        soup = bs(page.content, 'lxml')

        # Extraire les liens et titres des films
        links = [a['href'] for a in soup.find_all('a', class_='ipc-title-link-wrapper')]
        cleaned_links = [link.split('/')[2].split('?')[0].replace('tt', '') for link in links]

        logger.info("Liens IMDB nettoyés: %s", cleaned_links)

        task_instance.xcom_push(key="cleaned_links", value=cleaned_links)

    except requests.RequestException as e:
        logger.error(f"Erreur lors de la récupération de la page IMDb: {e}")

    finally:
        end_time = time.time()
        duration = end_time - start_time

        logger.info(f"Durée du scraping IMDb: {duration} secondes")

def genres_request(task_instance):
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
        task_instance.xcom_push(key="genres", value=genres)
        logger.info("Genres récupérés avec succès: %s", genres)


def api_tmdb_request(task_instance):
    """Effectue des requêtes à l'API TMDB pour récupérer les informations des films."""
    results = {}
    cleaned_links = task_instance.xcom_pull(task_ids="scrape_imdb_task", key="cleaned_links")
    genres = task_instance.xcom_pull(task_ids="get_genres_task", key="genres")
    logger.info("Liens nettoyés recus via XCom: %s", cleaned_links)
    logger.info("Genres recus via XCom: %s", genres)

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
                movie_info = data["movie_results"][0]
                release_date = movie_info["release_date"]
                release_year = release_date.split("-")[0]  # Extraire l'année

                results[str(index)] = {
                    "tmdb_id": movie_info["id"],
                    "title": movie_info["title"],
                    "genre_ids": movie_info['genre_ids'],
                    "imbd_id": movie_id,
                    "date": release_date,
                    "year": release_year,  # Ajouter l'année extraite
                    "genres": [genres[str(genre_id)] for genre_id in movie_info['genre_ids']]
                }

        else:
            results[str(index)] = {"error": f"Request failed with status code {response.status_code}"}

    task_instance.xcom_push(key="api_results", value=results)

def insert_data_movies(task_instance):
    """Insère les données des films dans la base de données."""
    start_time = time.time()
    api_results = task_instance.xcom_pull(task_ids="scrape_movies_infos_task", key="api_results")
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                for index, movie_data in api_results.items():
                    count = 0
                    # Exécuter la requête pour récupérer la valeur maximale de movieId
                    cur.execute("SELECT MAX(movieId) FROM movies")
                    max_movie_id = cur.fetchone()[0]
                    movieId = max_movie_id + 1
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
                    cur.execute("SELECT 1 FROM movies WHERE title = %s AND year = %s", (title, year))

                    if cur.fetchone() is None:  # Si le film n'existe pas déjà
                        count += 1
                        genres_str = ','.join(genres)  # Convertir la liste de genres en chaîne de caractères
                        # Insertion du film et récupération de l'ID inséré
                        cur.execute("""
                            INSERT INTO movies (movieId, title, genres, year)
                            VALUES (%s, %s, %s, %s)
                        """, (movieId, title, genres_str, year))

                        # Insertion du lien avec l'ID du film
                        cur.execute("""
                            INSERT INTO links (movieId, imdbId, tmdbId)
                            VALUES (%s, %s, %s)
                        """, (movieId, imdb_id, tmdb_id))

                        logger.info(f"Film inséré: {title} avec ID {movieId}")
                    else:
                        logger.info(f"Le film {title} existe déjà dans la base de données.")

                conn.commit()  # Valider les changements dans la base de données

                logger.info("Données insérées avec succès dans les tables movies & links.")

                logger.info(f"Nombre de films insérés: {count}")

    except Exception as e:
        logger.error(f"Erreur lors de la connexion à la base de données: {e}")

    finally:
        end_time = time.time()
        duration = end_time - start_time

        logger.info(f"Durée de l'insertion des données: {duration} secondes")

# Arguments par défaut pour le DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 11, 19),
}

# Création du DAG principal
dag_scraping_and_inserting_movies = DAG(
    dag_id='imdb_scraper_updating_db_dag',
    description='Scraping IMDb and updating database',
    tags=['antoine'],
    default_args=default_args,
    schedule_interval='@daily',
)

# Tâche pour récupérer les genres depuis TMDB
get_genres_task = PythonOperator(
    task_id='get_genres_task',
    python_callable=genres_request,
    dag=dag_scraping_and_inserting_movies,
)

# Tâche pour scraper IMDb et récupérer les liens
scrape_imdb_task = PythonOperator(
    task_id='scrape_imdb_task',
    python_callable=scrape_imdb_first_page,
    dag=dag_scraping_and_inserting_movies,
)

# Tâche pour récupérer les infos des films depuis TMDB
scrape_infos_task = PythonOperator(
    task_id='scrape_movies_infos_task',
    python_callable=api_tmdb_request,
    op_kwargs={'cleaned_links': '{{ task_instance.xcom_pull(task_ids="scrape_imdb_task") }}', 'genres': '{{ task_instance.xcom_pull(task_ids="get_genres_task") }}'},
    dag=dag_scraping_and_inserting_movies,
)

# Tâche pour insérer les données dans la base
insert_data_task = PythonOperator(
    task_id='insert_data_movies_task',
    python_callable=insert_data_movies,
    op_kwargs={
      'api_results': '{{ task_instance.xcom_pull(task_ids="scrape_movies_infos_task") }}',
   },
   dag=dag_scraping_and_inserting_movies,
)

# Définir l'ordre d'exécution des tâches dans le DAG
get_genres_task >> scrape_imdb_task >> scrape_infos_task >> insert_data_task