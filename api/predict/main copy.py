from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import pandas as pd
import os
import pickle
import dotenv
import mlflow
from mlflow.sklearn import load_model
from prometheus_fastapi_instrumentator import Instrumentator
from metrics import PREDICTION_REQUESTS, PREDICTION_LATENCY, MODEL_INFO
from prometheus_client import Counter, Histogram, Info
import time

dotenv.load_dotenv()

app = FastAPI()

Instrumentator().instrument(app).expose(app)


def load_recommender_model():
    try:
        # Essayer d'abord MLflow
        mlflow_uri = os.getenv("MLFLOW_TRACKING_URI", "http://tracking_server:5000")
        print(f"Tentative de connexion à MLflow sur : {mlflow_uri}")

        mlflow.set_tracking_uri(mlflow_uri)
        print("URI MLflow configuré")

        # Vérifier la connexion à MLflow
        try:
            mlflow.search_runs()
            print("Connexion à MLflow réussie")
        except Exception as e:
            print(f"Erreur de connexion à MLflow: {str(e)}")
            raise

        # Tenter de charger le modèle
        print("Tentative de chargement du modèle 'movie_recommender'")
        model = mlflow.sklearn.load_model("models:/movie_recommender/latest")
        print("Modèle chargé avec succès")

        MODEL_INFO.info({"model_name": "movie_recommender"})

        model_infos = {
            "mlflow_uri": mlflow_uri,
            "model_name": "movie_recommender",
            "model_version": "latest",
            "runs": mlflow.search_runs(),
        }

        return model, model_infos
    except Exception as e:
        print(f"Erreur détaillée lors du chargement du modèle MLflow: {str(e)}")
        raise


model, model_infos = load_recommender_model()


def make_predictions(genres, model):
    # genres is a string of 1 and 0, we need to split it into a list of integers
    genres = genres.split(",")
    genres = [float(genre) for genre in genres]
    genres = np.array(genres).reshape(1, -1)

    # Add the values to the dataframe with the columns
    columns = [
        "(no genres listed)",
        "Action",
        "Adventure",
        "Animation",
        "Children",
        "Comedy",
        "Crime",
        "Documentary",
        "Drama",
        "Fantasy",
        "Film-Noir",  # not in genre
        "Horror",
        "IMAX",  # not in genre
        "Musical",
        "Mystery",
        "Romance",
        "Sci-Fi",
        "Thriller",
        "War",
        "Western",
    ]
    genres = pd.DataFrame(genres, columns=columns)

    _, indices = model.kneighbors(genres)

    # Select 20 random numbers from each row
    selection = np.array(
        [np.random.choice(row, size=20, replace=False) for row in indices]
    )

    # Convert the numpy array to a list before returning
    return selection.tolist()


class UserInput(BaseModel):
    genres: str


@app.post("/recommend")
def recommend(user_input: UserInput):
    PREDICTION_REQUESTS.inc()
    start_time = time.time()
    recommendations = make_predictions(user_input.genres, model)
    end_time = time.time()
    PREDICTION_LATENCY.observe(end_time - start_time)
    return {"recommendations": recommendations}


@app.get("/model_info")
def model_info():
    return model_infos
