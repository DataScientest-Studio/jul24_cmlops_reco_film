from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import os
from supabase import create_client
from dotenv import load_dotenv
import time

# import logging

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

load_dotenv()
TMDB_API_TOKEN = os.environ.get("TMDB_API_TOKEN")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
DATE = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")


def genres_request(task_instance):
    """Effectue une requête à l'API TMDB pour récupérer les genres."""
    url = "https://api.themoviedb.org/3/genre/movie/list?language=en"

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {TMDB_API_TOKEN}",
    }

    print(TMDB_API_TOKEN)

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        genres = {str(genre["id"]): genre["name"] for genre in data["genres"]}
        task_instance.xcom_push(key="genres", value=genres)


def scrape_movies(task_instance):
    """Scrape les films dans la date de sortie spécifiée."""

    start_date = DATE
    end_date = DATE
    page = 1
    all_results = []

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {TMDB_API_TOKEN}",
    }

    # Première requête pour obtenir le nombre total de pages
    url = f"https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&page={page}&primary_release_date.gte={start_date}&primary_release_date.lte={end_date}&sort_by=primary_release_date.asc"
    response = requests.get(url, headers=headers)
    data = response.json()
    total_pages = data["total_pages"]
    all_results.extend(data["results"])

    time.sleep(2)

    while page < total_pages:
        page += 1
        url = f"https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&page={page}&primary_release_date.gte={start_date}&primary_release_date.lte={end_date}&sort_by=primary_release_date.asc"
        response = requests.get(url, headers=headers)
        data = response.json()
        all_results.extend(data["results"])

        time.sleep(2)

    complete_data = {
        "page": page,
        "results": all_results,
        "total_pages": total_pages,
        "total_results": len(all_results),
    }

    task_instance.xcom_push(key=f"movies_{DATE}", value=complete_data)


def transform_data(task_instance):
    """Transforme les données des films."""
    movies = task_instance.xcom_pull(
        key=f"movies_{DATE}", task_ids="scrape_movies_in_release_date_range_task"
    )
    genres = task_instance.xcom_pull(task_ids="get_genres_task", key="genres")

    movies_data = []
    for movie in movies["results"]:
        
        genre_names = []
        for genre_id in movie["genre_ids"]:
            genre_id = str(genre_id)
            if genre_id in genres:
                genre = genres[genre_id]
                if genre == "Science Fiction":
                    genre = "Sci-Fi"
                elif genre == "Music":
                    genre = "Musical" 
                elif genre == "Family":
                    genre = "Children"
                elif genre not in ["History", "TV Movie"]:
                    genre_names.append(genre)

        movie_data = {
            "title": movie["title"],
            "year": int(movie["release_date"].split("-")[0]),
            "genres": "|".join(genre_names) if genre_names else "(no genres listed)",
            "posterUrl": (
                f"https://image.tmdb.org/t/p/w500{movie['poster_path']}"
                if movie["poster_path"]
                else None
            ),
            "tmdbId": str(movie["id"]),
        }
        movies_data.append(movie_data)

    return movies_data


def insert_data_movies(task_instance):
    """Insère les données des films dans la base de données."""
    try:
        movies_data = task_instance.xcom_pull(task_ids="transform_data_task")
        if not movies_data:
            raise ValueError("Aucune donnée à insérer")

        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        supabase.table("movies").upsert(movies_data).execute()

        print(f"Données insérées avec succès: {len(movies_data)} films")
        return f"{len(movies_data)} films insérés avec succès"

    except Exception as e:
        print(f"Erreur générale: {str(e)}")
        raise


# Arguments par défaut pour le DAG
default_args = {
    "owner": "airflow",
    "start_date": datetime(2024, 11, 19),
    "retries": 2,
    "retry_delay": timedelta(seconds=20),
}

dag_scraping_and_inserting_movies = DAG(
    dag_id="scraping_tmdb",
    description="Scraping avec l'api tmdb",
    tags=["project", "scraping", "datascientest"],
    default_args=default_args,
    schedule_interval="0 10 * * *",  # Exécution à 10h00 tous les jours
    catchup=False,
)

get_genres_task = PythonOperator(
    task_id="get_genres_task",
    python_callable=genres_request,
    dag=dag_scraping_and_inserting_movies,
)

scrape_movies_in_release_date_range_task = PythonOperator(
    task_id="scrape_movies_in_release_date_range_task",
    python_callable=scrape_movies,
    dag=dag_scraping_and_inserting_movies,
)

transform_data_task = PythonOperator(
    task_id="transform_data_task",
    python_callable=transform_data,
    dag=dag_scraping_and_inserting_movies,
)

insert_data_task = PythonOperator(
    task_id="insert_data_movies_task",
    python_callable=insert_data_movies,
    dag=dag_scraping_and_inserting_movies,
)

(
    get_genres_task
    >> scrape_movies_in_release_date_range_task
    >> transform_data_task
    >> insert_data_task
)
