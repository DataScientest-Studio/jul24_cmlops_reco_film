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

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

POSTGRES_USER= os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD= os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB= os.getenv('POSTGRES_DB')
POSTGRES_HOST= os.getenv('POSTGRES_HOST')
POSTGRES_PORT= os.getenv('POSTGRES_PORT')

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
        conn.rollback()
        raise
    finally:
        if conn is not None:
            conn.close()
            print("Connexion à la base de données fermée")

def scrape_imdb():
    """Scrape les données des films depuis IMDb et les insère dans Supabase."""
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

    # Connexion à postgres pour insérer les données
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Créer la table movies si elle n'existe pas
            cur.execute("""
                CREATE TABLE IF NOT EXISTS movies (
                    movieId SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    genres TEXT,
                    year INT
                )
            """)

            # Créer la table links si elle n'existe pas
            cur.execute("""
                CREATE TABLE IF NOT EXISTS links (
                        id SERIAL PRIMARY KEY,
                        movieId INT REFERENCES movies(movieId),
                        imdbId INT,
                        tmdbId INT)
                )
            """)

            # Insérer les données des films dans la table movies
            for title, genres, year in zip(cleaned_titles, genres_list, year_list):
                cur.execute("INSERT INTO movies (title, genres, year) VALUES (%s, %s, %s)", (title, genres, year))
            # Insérer les données des films dans la table links
            for imdb_id in cleaned_links:
                cur.execute("INSERT INTO links (imdbId) VALUES (%s)", (imdb_id,))
            conn.commit()

            print("Données insérées avec succès dans la base de données.")

def export_table_to_csv(table_name, csv_file_path):
    """Exporte une table de postgres vers un fichier CSV."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM {table_name}")
            rows = cur.fetchall()
            df = pd.DataFrame(rows)
            df.to_csv(csv_file_path, index=False)
            print(f"Table {table_name} exportée vers {csv_file_path}")

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

# Tâche pour exporter la table movies vers CSV
update_movies_task = PythonOperator(
    task_id='update_movies_task',
    python_callable=export_table_to_csv,
    dag=dag,
    op_kwargs={"table_name": "movies", "csv_file_path": "/opt/airflow/data/raw/processed_movies.csv"}
)

# Tâche pour exporter la table links vers CSV
update_links_task = PythonOperator(
    task_id='update_links_task',
    python_callable=export_table_to_csv,
    dag=dag,
    op_kwargs={"table_name": "links", "csv_file_path": "/opt/airflow/data/raw/processed_links.csv"}
)

# Définir l'ordre d'exécution des tâches dans le DAG
scrape_task >> update_movies_task >> update_links_task

if __name__ == "__main__":
    from airflow.utils.state import State
    from airflow.models import DagBag

    dag_bag = DagBag()
    dag = dag_bag.get_dag(dag_id='imdb_scraper_dag')
    dag.clear()

    # Exécuter les tâches du DAG
    for task in dag.tasks:
        task.run(ignore_ti_state=True)

    # Vérifier l'état des tâches
    for task in dag.tasks:
        ti = dag.get_task_instance(task.task_id)
        assert ti.state == State.SUCCESS, f"Tâche {task.task_id} échouée"
