import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
import os
import pickle
import mlflow
import psycopg2
from dotenv import load_dotenv
from contextlib import contextmanager
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator


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

# Configuration de MLflow
mlflow.set_tracking_uri("http://mlflow_webserver:5000")
EXPERIMENT_NAME = "Movie_Recommendation_Experiment"
time = datetime.now()
run_name = f"{time}_Modèle KNN"

def create_X(df):
    """Generates a sparse user-item rating matrix."""
    M = df['userid'].nunique()
    N = df['movieid'].nunique()

    user_mapper = dict(zip(np.unique(df["userid"]), list(range(M))))
    movie_mapper = dict(zip(np.unique(df["movieid"]), list(range(N))))

    user_index = [user_mapper[i] for i in df['userid']]
    item_index = [movie_mapper[i] for i in df['movieid']]

    X = csr_matrix((df["rating"], (user_index, item_index)), shape=(M, N))

    return X

def train_model(df, k=10):
    """Trains the KNN model on the training data."""
    X = create_X(df)

    X = X.T  # Transpose to have users in rows

    kNN = load_model('model_KNN.pkl')

    model = kNN.fit(X)

    return model

def save_model(model, filepath: str) -> None:
    """Sauvegarde le modèle entraîné dans un fichier."""
    directory = os.path.join(filepath, 'model_KNN.pkl')
    with open(directory, 'wb') as file:
        pickle.dump(model, file)
        print(f'Modèle sauvegardé sous {filepath}/model_KNN.pkl')

def run_training(**kwargs):
    """Main function to train the model."""
     # Démarrer un nouveau run dans MLflow
    with mlflow.start_run(run_name=run_name) as run:
        # Load data
        ratings = fetch_latest_ratings()
        # Train KNN model
        model_knn = train_model(ratings)
        save_model(model_knn, '/opt/airflow/models/')

        # Enregistrer les métriques dans MLflow pour suivi ultérieur
        mlflow.log_param("n_neighbors", 11)
        mlflow.log_param("algorithm", "brute")
        mlflow.log_param("metric", "cosine")

# Define Airflow DAG
my_dag = DAG(
    dag_id='KNN_train_model',
    description='KNN Model for Movie Recommendation',
    tags=['antoine'],
    schedule_interval='@daily',
    default_args={
        'owner': 'airflow',
        'start_date': datetime(2024, 11, 22),
    }
)

# Create a task to train the model and evaluate its performance
train_task = PythonOperator(
    task_id='train_model',
    python_callable=run_training,
    dag=my_dag,
)

train_task_kube = KubernetesPodOperator(
    task_id="train_model_kube",
    name="train_model_kube",
    namespace="airflow",
    image="airflow-mlflow:latest",
    cmds=["python", "predict_knn_model.py"],
    get_logs=True,
    env_vars={
        'POSTGRES_USER': POSTGRES_USER,
        'POSTGRES_PASSWORD': POSTGRES_PASSWORD,
        'POSTGRES_DB': POSTGRES_DB,
        'POSTGRES_HOST': POSTGRES_HOST,
        'POSTGRES_PORT': POSTGRES_PORT,
    },
    dag=my_dag
)

# Define dependencies between tasks
train_task >> train_task_kube