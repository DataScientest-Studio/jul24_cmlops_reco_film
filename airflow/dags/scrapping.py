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
from contextlib import contextmanager  # Ajout du module contextlib
import logging
from airflow.utils.dates import days_ago
from airflow.hooks.base_hook import BaseHook
import time

# Configurer le logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

POSTGRES_USER= os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD= os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB= os.getenv('POSTGRES_DB')
POSTGRES_HOST= os.getenv('POSTGRES_HOST')
POSTGRES_PORT= os.getenv('POSTGRES_PORT')

@contextmanager  # Ajout du décorateur contextmanager
def get_db_connection():
    """
    Gestionnaire de contexte pour la connexion à la base de données.
    Ouvre une connexion et la ferme automatiquement après utilisation.

    Utilisation:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM table")
    """
    conn = None
    try:
        conn = psycopg2.connect(
            database=POSTGRES_DB,
            host=POSTGRES_HOST,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            port=POSTGRES_PORT
        )
        print("Connection à la base de données OK")
        yield conn
    except psycopg2.Error as e:
        print(f"Erreur lors de la connexion à la base de données: {e}")
        raise
    finally:
        if conn is not None:
            conn.close()
            print("Connexion à la base de données fermée")

def scrape_imdb():
    """Scrape les données des films depuis IMDb et les insère dans Supabase."""
    start_time = time.time()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Récupérer la page des box-offices d'IMDb
    page = requests.get("https://www.imdb.com/chart/boxoffice", headers=headers)
    soup = bs(page.content, 'lxml')

    # Extraire les liens et titres des films
    links = [a['href'] for a in soup.find_all('a', class_='ipc-title-link-wrapper')]
    titles = [h3.get_text() for h3 in soup.find_all('h3', class_='ipc-title__text')[1:11]]

    # Nettoyer les titres et extraire les IDs IMDb
    cleaned_titles = [re.sub(r'^\d+\.\s*', '', title) for title in titles]
    cleaned_links = [link.split('/')[2].split('?')[0].replace('tt', '') for link in links]


    genres_list, year_list = [], []

    # Boucle pour récupérer les détails de chaque film
    for imdb_ref in cleaned_links:
        movie_page = requests.get(f"http://www.imdb.com/title/tt{imdb_ref}/", headers=headers)
        soup_movie = bs(movie_page.content, 'lxml')

        # Récupérer les genres du film
        genres = soup_movie.find_all('span', class_='ipc-chip__text')
        movie_genres = [i.text for i in genres[:-1]]
        genres_list.append(movie_genres)

        # Récupérer l'année de sortie du film
        year_elem = soup_movie.find('a', {
            'class': 'ipc-link ipc-link--baseAlt ipc-link--inherit-color',
            'tabindex': '0',
            'aria-disabled': 'false',
            'href': f'/title/tt{imdb_ref}/releaseinfo?ref_=tt_ov_rdat'
        })
        year_list.append(year_elem.text if year_elem else None)

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                try:
                    # Récupération du dernier movieId
                    cur.execute("SELECT COALESCE(MAX(movieId), 0) FROM movies")
                    last_movie_id = cur.fetchone()[0]

                    # Liste pour stocker les insertions à effectuer
                    insert_movies = []
                    insert_links = []

                    for title, genres, year, link in zip(cleaned_titles, genres_list, year_list, cleaned_links):
                        cur.execute("SELECT 1 FROM movies WHERE title = %s AND year = %s", (title, year))
                        if cur.fetchone() is None:
                            last_movie_id += 1
                            genres_str = ','.join(genres)  # Convertir la liste de genres en chaîne de caractères
                            insert_movies.append((title, genres_str, year))
                            insert_links.append((last_movie_id, link))
                            logger.info(f"Titres insérés: {insert_movies}")
                            logger.info(f"Liens insérés: {insert_links}")
                        else:
                            print(f"Le film {title} existe déjà dans la base de données.")
                    # Insertion des films
                    if insert_movies:
                        cur.executemany("""
                            INSERT INTO movies (title, genres, year)
                            VALUES (%s, %s, %s)
                        """, insert_movies)

                    # Insertion des liens
                    if insert_links:
                        cur.executemany("""
                            INSERT INTO links (movieId, imdbId)
                            VALUES (%s, %s)
                        """, insert_links)

                    conn.commit()
                    logger.info("Données insérées avec succès dans les tables movies & links.")
                    # Envoyer la métrique du nombre de films insérés
                    statsd = BaseHook.get_connection('statsd_default')
                    statsd.gauge('imdb_scraper.movies_inserted', len(insert_movies))

                except Exception as e:
                    conn.rollback()
                    logger.error(f"Une erreur est survenue : {e}")
                    raise
    finally:
        end_time = time.time()
        duration = end_time - start_time
        # Envoyer la métrique de durée d'exécution
        statsd.gauge('imdb_scraper.duration', duration)
        # Envoyer la métrique de succès/échec
        statsd.increment('imdb_scraper.success' if not e else 'imdb_scraper.failure')

# Arguments par défaut pour le DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 11, 19),
}

# Création du DAG
dag = DAG(
    dag_id='imdb_scraper_dag',
    description='Scraping IMDb and updating datasets',
    tags=['antoine'],
    default_args=default_args,
    schedule_interval='@daily',
)

# Tâche pour scraper IMDb
scrape_task = PythonOperator(
    task_id='scrape_imdb_task',
    python_callable=scrape_imdb,
    dag=dag,
)

# Définir l'ordre d'exécution des tâches dans le DAG
scrape_task
