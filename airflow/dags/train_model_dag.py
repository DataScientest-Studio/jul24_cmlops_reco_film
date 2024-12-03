from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from supabase import create_client
import os
import mlflow
import numpy as np
import dotenv
import time
import requests

dotenv.load_dotenv()

# Configuration de MLflow
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow_server:5000")
EXPERIMENT_NAME = "movie_recommender"
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Définition des arguments par défaut
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

# Ajouter ces constantes en haut du fichier
TEMP_DATA_DIR = "/tmp/movie_recommender"
RAW_DATA_PATH = os.path.join(TEMP_DATA_DIR, "raw_data.parquet")
MATRIX_PATH = os.path.join(TEMP_DATA_DIR, "movie_matrix.parquet")


def setup_mlflow():
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
    if experiment is None:
        mlflow.create_experiment(EXPERIMENT_NAME)
    mlflow.set_experiment(EXPERIMENT_NAME)


def fetch_movie_data():
    try:
        # Créer le répertoire temporaire s'il n'existe pas
        os.makedirs(TEMP_DATA_DIR, exist_ok=True)

        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        response = supabase.table("movies").select("movieId,genres").execute()

        # Convertir en DataFrame et sauvegarder
        df = pd.DataFrame(response.data)
        df.to_parquet(RAW_DATA_PATH)

        return RAW_DATA_PATH
    except Exception as e:
        raise Exception(f"Erreur lors de la récupération des données : {str(e)}")


def prepare_movie_matrix(**context):
    try:
        # Lire les données brutes
        raw_data_path = context["task_instance"].xcom_pull(task_ids="fetch_data")
        movies_data = pd.read_parquet(raw_data_path)

        # Préparer la matrice
        genres = movies_data["genres"].str.get_dummies(sep="|")
        movie_matrix = pd.concat([movies_data[["movieId"]], genres], axis=1)

        # Sauvegarder la matrice préparée
        movie_matrix.to_parquet(MATRIX_PATH)

        return MATRIX_PATH
    except Exception as e:
        raise Exception(f"Erreur lors de la préparation de la matrice : {str(e)}")


def train_model_task(**context):
    try:
        setup_mlflow()

        matrix_path = context["task_instance"].xcom_pull(task_ids="prepare_matrix")
        movie_matrix = pd.read_parquet(matrix_path)

        with mlflow.start_run() as run:

            mlflow.log_artifact(matrix_path, "data")

            params = {"n_neighbors": 20, "algorithm": "ball_tree"}
            mlflow.log_params(params)

            # Entraînement du modèle
            nbrs = NearestNeighbors(
                n_neighbors=params["n_neighbors"], algorithm=params["algorithm"]
            ).fit(movie_matrix.drop("movieId", axis=1))

            # Calcul et log des métriques
            distances, _ = nbrs.kneighbors(movie_matrix.drop("movieId", axis=1))

            avg_distance = np.mean(distances)
            min_distance = np.min(distances[:, 1:])  # Exclure la distance à soi-même
            max_distance = np.max(distances)
            std_distance = np.std(distances)

            # Log des métriques
            mlflow.log_metric("average_neighbor_distance", avg_distance)
            mlflow.log_metric("min_neighbor_distance", min_distance)
            mlflow.log_metric("max_neighbor_distance", max_distance)
            mlflow.log_metric("std_neighbor_distance", std_distance)

            # Log du modèle directement dans MLflow/MinIO
            mlflow.sklearn.log_model(
                sk_model=nbrs,
                artifact_path="model",
                registered_model_name="movie_recommender",
            )

            # Stockage du run_id dans XCom pour utilisation ultérieure
            context["task_instance"].xcom_push(
                key="mlflow_run_id", value=run.info.run_id
            )

            # Nettoyer les fichiers temporaires
            for temp_file in [RAW_DATA_PATH, MATRIX_PATH]:
                if os.path.exists(temp_file):
                    os.remove(temp_file)

    except Exception as e:
        # Nettoyer en cas d'erreur
        for temp_file in [RAW_DATA_PATH, MATRIX_PATH]:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        raise Exception(f"Erreur lors de l'entraînement du modèle : {str(e)}")


def challenging_champion_task(**context):
    setup_mlflow()

    run_id = context["task_instance"].xcom_pull(
        key="mlflow_run_id", task_ids="train_model"
    )

    client = mlflow.tracking.MlflowClient()

    try:
        mlflow.search_runs().empty  # Vérifie si le DataFrame est vide
        print("Connexion à MLflow réussie")
    except Exception as e:
        raise Exception(f"Connexion à MLflow échouée: {str(e)}")

    filter_string = f"run_id='{run_id}'"
    print(f"Filter string : {filter_string}")

    max_attempts = 5
    wait_time = 10

    for attempt in range(max_attempts):
        print(f"Tentative {attempt + 1}/{max_attempts} de récupération du modèle")
        challengers = client.search_model_versions(filter_string)

        if challengers:
            print(f"Modèle trouvé après {attempt + 1} tentatives")
            break

        print(f"Modèle non trouvé, attente de {wait_time} secondes")
        time.sleep(wait_time)
    else:
        raise Exception("Impossible de trouver le modèle après plusieurs tentatives")

    challenger = challengers[0]

    challenger_av_d = mlflow.get_run(run_id=run_id).data.metrics.get(
        "average_neighbor_distance"
    )

    try:
        champion = client.get_model_version_by_alias(
            name="movie_recommender", alias="champion"
        )
    except:
        champion = None

    if champion:
        champion_av_d = mlflow.get_run(run_id=champion.run_id).data.metrics.get(
            "average_neighbor_distance"
        )

        if challenger_av_d <= champion_av_d:
            client.set_registered_model_alias(
                name="movie_recommender", alias="champion", version=challenger.version
            )
            print(
                f"Le challenger {challenger.version} est meilleur que le champion {champion.version}. Nous avons un nouveau champion!"
            )
        else:
            print(
                f"Le challenger {challenger.version} est moins performant que le champion {champion.version}. Le champion reste champion."
            )
        print(f"Average neighbor distance champion : {champion_av_d}")
        print(f"Average neighbor distance challenger : {challenger_av_d}")
    else:
        print("Aucun champion trouvé")
        # S'il n'y a pas de champion, le challenger devient automatiquement le champion
        client.set_registered_model_alias(
            name="movie_recommender", alias="champion", version=challenger.version
        )
        print(f"Modèle {challenger.version} défini comme premier champion")


def api_predict_reload_model_task(**context):

    reload_model_url = "http://api-predict:8000/reload_model"
    reload_model = requests.post(reload_model_url)
    if reload_model.status_code == 200:
        print("Modèle rechargé avec succès")
    else:
        print(f"Erreur lors du rechargement du modèle: {reload_model.json()}")


# Ajouter une tâche de nettoyage de secours
def cleanup_temp_files():
    for temp_file in [RAW_DATA_PATH, MATRIX_PATH]:
        if os.path.exists(temp_file):
            os.remove(temp_file)
    if os.path.exists(TEMP_DATA_DIR):
        os.rmdir(TEMP_DATA_DIR)


# Création du DAG
with DAG(
    "movie_recommender_training",
    tags=["datascientest", "project", "model", "training"],
    default_args=default_args,
    description="DAG pour entraîner le modèle de recommandation de films avec MLflow",
    schedule_interval="0 20 * * *",  # Exécution à 20h00 tous les jours
    catchup=False,
) as dag:

    fetch_data = PythonOperator(task_id="fetch_data", python_callable=fetch_movie_data)

    prepare_matrix = PythonOperator(
        task_id="prepare_matrix", python_callable=prepare_movie_matrix
    )

    train_model = PythonOperator(
        task_id="train_model", python_callable=train_model_task
    )

    challenging_champion = PythonOperator(
        task_id="challenging_champion",
        python_callable=challenging_champion_task,
        trigger_rule="all_success",
    )

    reload_model = PythonOperator(
        task_id="reload_model",
        python_callable=api_predict_reload_model_task,
        trigger_rule="all_success",
    )

    cleanup = PythonOperator(
        task_id="cleanup",
        python_callable=cleanup_temp_files,
        trigger_rule="all_done",  # S'exécute même si les tâches précédentes ont échoué
    )

    # Définition de l'ordre des tâches
    (
        fetch_data
        >> prepare_matrix
        >> train_model
        >> challenging_champion
        >> reload_model
        >> cleanup
    )
