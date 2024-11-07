from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import numpy as np
import pandas as pd

app = FastAPI()

# Charger le modèle une seule fois au démarrage de l'application
with open("model.pkl", "rb") as filehandler:
    model = pickle.load(filehandler)


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
        "Film-Noir",
        "Horror",
        "IMAX",
        "Musical",
        "Mystery",
        "Romance",
        "Sci-Fi",
        "Thriller",
        "War",
        "Western",
    ]
    genres = pd.DataFrame(genres, columns=columns)

    # Calculate nearest neighbors
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
    # Model prediction logic here
    recommendations = make_predictions(user_input.genres, model)
    return {"recommendations": recommendations}
