from fastapi import FastAPI, Request
from pydantic import BaseModel
import numpy as np
import pandas as pd
import os
import pickle
import dotenv
import mlflow
from metrics import (
    PREDICTION_REQUESTS,
    PREDICTION_LATENCY,
    MODEL_INFO,
    MODEL_RELOAD_COUNTER,
    API_REQUESTS_TOTAL,
    ACTIVE_REQUESTS,
)
import time
from prometheus_client import make_asgi_app
import requests

dotenv.load_dotenv()

app = FastAPI()

# Créer une endpoint Prometheus séparée
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Variables globales pour le modèle et les infos
model = None
model_infos = None

MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "http://tracking_server:5000")


def load_model_from_mlflow():
    print(f"Tentative de connexion à MLflow sur : {MLFLOW_URI}")

    mlflow.set_tracking_uri(MLFLOW_URI)

    try:
        response = requests.get(MLFLOW_URI, timeout=5)
        response.raise_for_status()
        mlflow.search_runs()
        print("Connexion à MLflow réussie")

        client = mlflow.tracking.MlflowClient()
        model_champion = client.get_model_version_by_alias(
            name="movie_recommender", alias="champion"
        )
        model_version = model_champion.version
        model = mlflow.sklearn.load_model(f"models:/movie_recommender/{model_version}")
        print("Modèle chargé avec succès depuis MLflow")

        return model, model_version
    except requests.exceptions.RequestException as e:
        print(f"Erreur de connexion à MLflow: {str(e)}")
        raise


def load_model_locally():
    print("Tentative de chargement du modèle local")

    try:
        with open("model.pkl", "rb") as f:
            model = pickle.load(f)
        print("Modèle local chargé avec succès")
        return model, "local"
    except Exception as e:
        print(f"Erreur lors du chargement du modèle local: {str(e)}")
        raise


def load_recommender_model():
    try:
        model, model_version = load_model_from_mlflow()
        source = "mlflow"
    except Exception:
        model, model_version = load_model_locally()
        source = "local"

    model_infos = {
        "model_name": "movie_recommender",
        "model_version": model_version,
        "source": source,
    }

    MODEL_INFO.info(model_infos)

    return model, model_infos


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


@app.on_event("startup")
async def startup_event():
    global model, model_infos
    model, model_infos = load_recommender_model()


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


@app.post("/reload_model")
async def reload_model():
    global model, model_infos
    try:
        model, model_infos = load_recommender_model()
        MODEL_RELOAD_COUNTER.inc()
        return {"status": "success", "message": "Modèle rechargé avec succès"}
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erreur lors du rechargement du modèle: {str(e)}",
        }


@app.middleware("http")
async def track_requests(request: Request, call_next):
    ACTIVE_REQUESTS.inc()
    start_time = time.time()

    response = await call_next(request)

    ACTIVE_REQUESTS.dec()
    API_REQUESTS_TOTAL.labels(
        method=request.method,
        endpoint=request.url.path,
        status_code=response.status_code,
    ).inc()

    return response


@app.get("/health")
def health_check():
    return {"status": "ok"}
