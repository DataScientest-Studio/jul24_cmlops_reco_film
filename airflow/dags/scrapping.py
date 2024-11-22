from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import re
import os
from dotenv import load_dotenv
import psycopg2 as psycopg2_binary
from contextlib import contextmanager
import logging
from airflow.utils.dates import days_ago
from airflow.hooks.base_hook import BaseHook
import time
from airflow.exceptions import AirflowNotFoundException

# Configurer le logger pour suivre les événements et les erreurs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')
tmdb_token = os.getenv("TMDB_API_TOKEN")

@contextmanager
def get_db_connection():
    """Gestionnaire de contexte pour la connexion à la base de données.
    Ouvre une connexion et la ferme automatiquement après utilisation.
    """
    conn = None
    try:
        # Établir la connexion à la base de données PostgreSQL
        conn = psycopg2_binary.connect(
            database=POSTGRES_DB,
            host=POSTGRES_HOST,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            port=POSTGRES_PORT
        )
        logger.info("Connection à la base de données OK")
        yield conn  # Retourner la connexion pour utilisation dans le bloc 'with'
    except psycopg2_binary.Error as e:
        logger.error(f"Erreur lors de la connexion à la base de données: {e}")
        raise  # Lever l'exception si une erreur se produit
    finally:
        if conn is not None:
            conn.close()  # Fermer la connexion à la fin du bloc 'with'
            logger.info("Connexion à la base de données fermée")

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

        try:
            statsd = BaseHook.get_connection('statsd_default')  # Initialiser statsd pour le suivi des métriques
            statsd.gauge('imdb_scraper.duration', duration)
            statsd.increment('imdb_scraper.success' if not e else 'imdb_scraper.failure')
        except AirflowNotFoundException:
            logger.warning("La connexion 'statsd_default' n'est pas définie.")

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
                results[str(index)] = {
                    "movieId": movie_info["id"],
                    "title": movie_info["title"],
                    "genre_ids": movie_info['genre_ids'],
                    "imbd_number": movie_id,
                }
                results[str(index)]["genres"] = [genres[str(genre_id)] for genre_id in movie_info['genre_ids']]

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
                    # Vérifier si une erreur a été retournée pour ce film
                    if "error" in movie_data:
                        logger.error(f"Erreur pour le film index {index}: {movie_data['error']}")
                        continue

                    title = movie_data["title"]
                    genres = movie_data["genres"]
                    imdb_number = movie_data["imbd_number"]

                    # Éviter les doublons dans la base de données
                    cur.execute("SELECT 1 FROM movies WHERE title = %s", (title,))

                    if cur.fetchone() is None:  # Si le film n'existe pas déjà
                        genres_str = ','.join(genres)  # Convertir la liste de genres en chaîne de caractères

                        # Insertion du film et récupération de l'ID inséré
                        cur.execute("""
                            INSERT INTO movies (title, genres)
                            VALUES (%s, %s)
                            RETURNING movieId
                        """, (title, genres_str))

                        new_movie_id = cur.fetchone()[0]  # Récupération de l'ID du film nouvellement inséré

                        # Insertion du lien avec l'ID du film
                        cur.execute("""
                            INSERT INTO links (movieId, imdbId)
                            VALUES (%s, %s)
                        """, (new_movie_id, imdb_number))

                        logger.info(f"Film inséré: {title} avec ID {new_movie_id}")
                    else:
                        logger.info(f"Le film {title} existe déjà dans la base de données.")

                conn.commit()  # Valider les changements dans la base de données

                logger.info("Données insérées avec succès dans les tables movies & links.")

                # Envoyer la métrique du nombre de films insérés
                try:
                    statsd = BaseHook.get_connection('statsd_default')
                    statsd.gauge('insert_db.movies_inserted', len(api_results))  # Compte total des titres traités

                except AirflowNotFoundException:
                    logger.warning("La connexion 'statsd_default' n'est pas définie.")

                except Exception as e:
                    logger.error(f"Erreur lors de l'envoi des métriques: {e}")

    except Exception as e:
        logger.error(f"Erreur lors de la connexion à la base de données: {e}")

    finally:
        end_time = time.time()
        duration = end_time - start_time

        try:
            statsd = BaseHook.get_connection('statsd_default')  # Initialiser statsd pour le suivi des métriques
            statsd.gauge('insert_db.duration', duration)
            statsd.increment('insert_db.success' if not e else 'insert_db.failure')

        except AirflowNotFoundException:
            logger.warning("La connexion 'statsd_default' n'est pas définie.")

        except Exception as e:
            logger.error(f"Erreur lors de l'envoi des métriques de durée: {e}")

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