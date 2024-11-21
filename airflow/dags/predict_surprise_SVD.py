import numpy as np
import pandas as pd
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import os
from surprise import Dataset, Reader
from surprise.prediction_algorithms.matrix_factorization import SVD
from surprise.model_selection import train_test_split
from surprise import accuracy
import mlflow
import pickle
from datetime import datetime
import psycopg2
from dotenv import load_dotenv
from contextlib import contextmanager

# Charger les variables d'environnement à partir du fichier .env
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

# Configuration de MLflow
mlflow.set_tracking_uri("http://mlflow_webserver:5000")
EXPERIMENT_NAME = "Movie_Recommendation_Experiment"
time = datetime.now()
run_name = f"{time}_Modèle SVD"

def load_model(pkl_files, directory = "/opt/airflow/models") :
    """Charge le modèle à partir d'un répertoire."""
    # Vérifier si le répertoire existe
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Le répertoire {directory} n'existe pas.")
    # Charger le modèle
    filepath = os.path.join(directory, pkl_files)
    with open(filepath, 'rb') as file:
        model = pickle.load(file)
        print(f'Modèle chargé depuis {filepath}')
    return model

def fetch_latest_ratings() -> pd.DataFrame:
    """Récupère 25 % des derniers enregistrements de la table ratings et les transforme en DataFrame."""
    query = """
    SELECT userId, movieId, rating
    FROM ratings
    ORDER BY id DESC
    LIMIT (SELECT COUNT(*) FROM ratings) * 0.25
    """
    try:
        with get_db_connection() as conn:
            df = pd.read_sql_query(query, conn)
            print("Derniers enregistrements récupérés")
            return df
    except Exception as e:
        print(f"Erreur lors de la récupération des enregistrements: {e}")
        raise

def train_model() -> tuple:
    """Entraîne le modèle de recommandation sur les données fournies et retourne le modèle et son RMSE."""
    # Démarrer un nouveau run dans MLflow
    with mlflow.start_run(run_name=run_name) as run:
        # Charger les données d'évaluation des films
        ratings = fetch_latest_ratings()

        # Préparer les données pour Surprise
        reader = Reader(rating_scale=(0.5, 5))
        data = Dataset.load_from_df(ratings[['userId', 'movieId', 'rating']], reader=reader)

        # Diviser les données en ensembles d'entraînement et de test
        trainset, testset = train_test_split(data, test_size=0.15)

        # Créer et entraîner le modèle SVD
        model = load_model('model_SVD.pkl')

        model.fit(trainset)

        # Tester le modèle sur l'ensemble de test et calculer RMSE
        predictions = model.test(testset)
        acc = accuracy.rmse(predictions)
        # Arrondir à 2 chiffres après la virgule
        acc_rounded = round(acc, 2)

        print("Valeur de l'écart quadratique moyen (RMSE) :", acc_rounded)

        # Enregistrer les métriques dans MLflow pour suivi ultérieur
        mlflow.log_param("n_factors", 150)
        mlflow.log_param("n_epochs", 30)
        mlflow.log_param("lr_all", 0.01)
        mlflow.log_param("reg_all", 0.05)
        # Arrondir à 2 chiffres après la virgule
        acc_rounded = round(acc, 2)

        print("Valeur de l'écart quadratique moyen (RMSE) :", acc_rounded)

        # Enregistrer les métriques dans MLflow pour suivi ultérieur
        mlflow.log_param("n_factors", 150)
        mlflow.log_param("n_epochs", 30)
        mlflow.log_param("lr_all", 0.01)
        mlflow.log_param("reg_all", 0.05)

        """Récupère le dernier RMSE enregistré dans MLflow."""
        mlflow.set_experiment(EXPERIMENT_NAME)

        # Récupérer les dernières exécutions triées par RMSE décroissant, en prenant la première (meilleure)
        runs = mlflow.search_runs(order_by=["metrics.rmse desc"], max_results=1)
        print("Chargement des anciens RMSE pour comparaison")

        if not runs.empty:
            last_rmse = runs.iloc[0]["metrics.rmse"]
        else:
            last_rmse = float('inf')  # Si aucun run n'est trouvé, retourner une valeur infinie

        print(f"Meilleur RMSE actuel: {last_rmse}, Nouveau RMSE: {acc_rounded}")

        directory = '/opt/airflow/models/model_SVD.pkl'

        with open(directory, 'wb') as file:
            pickle.dump(model, file)
            print(f'Modèle sauvegardé sous {directory}')

# Définition du DAG Airflow

svd_dag = DAG(
    dag_id='SVD_train_model',
    description='SVD Model for Movie Recommendation',
    tags=['antoine'],
    schedule_interval='@daily',
    default_args={
        'owner': 'airflow',
        'start_date': datetime(2024, 11, 3),
    }
)

# Tâches du DAG

train_task = PythonOperator(
   task_id='train_model',
   python_callable=train_model,
   dag=svd_dag,
)
