import pandas as pd
import os
from surprise import Dataset, Reader
from surprise.prediction_algorithms.matrix_factorization import SVD
from surprise.model_selection import train_test_split
from surprise import accuracy
import pickle

def read_ratings(ratings_csv: str, data_dir: str = "/jul24_cmlops_reco_film/ml/data/processed/") -> pd.DataFrame:
    """Lit le fichier CSV contenant les évaluations des films."""
    try:
        # Lire le fichier CSV et retourner un DataFrame Pandas
        data = pd.read_csv(os.path.join(data_dir, ratings_csv))
        print("Dataset ratings loaded")
        return data
    except Exception as e:
        print(f"Error loading data: {e}")
        raise

def train_model() -> tuple:
    """Entraîne le modèle de recommandation sur les données fournies et retourne le modèle et son RMSE."""
    # Charger les données d'évaluation des films
    ratings = read_ratings('processed_ratings.csv')
    # Préparer les données pour Surprise
    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(ratings[['userId', 'movieId', 'rating']], reader=reader)

    # Diviser les données en ensembles d'entraînement et de test
    trainset, testset = train_test_split(data, test_size=0.25)

    # Créer et entraîner le modèle SVD
    model = SVD(n_factors=150, n_epochs=30, lr_all=0.01, reg_all=0.05)
    model.fit(trainset)

    # Tester le modèle sur l'ensemble de test et calculer RMSE
    predictions = model.test(testset)
    acc = accuracy.rmse(predictions)
    # Arrondir à 2 chiffres après la virgule
    acc_rounded = round(acc, 2)

    print("Valeur de l'écart quadratique moyen (RMSE) :", acc_rounded)

    directory = '/ml/models/model_svd.pkl'

    with open(directory, 'wb') as file:
        pickle.dump(model, file)
        print(f'Modèle sauvegardé sous {directory}')


if __name__ == "__main__":
   train_model()