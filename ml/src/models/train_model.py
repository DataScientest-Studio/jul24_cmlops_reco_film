import os
import pandas as pd
from surprise import Dataset, Reader
from surprise.prediction_algorithms.matrix_factorization import SVD
from surprise.model_selection import train_test_split
from surprise import accuracy
import pickle
from datetime import datetime
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
import numpy as np


def read_ratings(ratings_csv: str) -> pd.DataFrame:
    """Lit le fichier CSV contenant les évaluations des films et retourne un DataFrame Pandas.

    Args:
        ratings_csv (str): Chemin vers le fichier CSV des évaluations.

    Returns:
        pd.DataFrame: DataFrame contenant les données des évaluations.

    Raises:
        FileNotFoundError: Si le fichier CSV n'est pas trouvé.
        pd.errors.EmptyDataError: Si le fichier CSV est vide.
        pd.errors.ParserError: Si le fichier CSV ne peut pas être analysé.
    """

    # Obtenir le répertoire du script actuel
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Construire le chemin vers le répertoire contenant les données traitées
    data_dir = os.path.join(base_dir, '..', '..', 'data', 'processed')

    # Construire le chemin complet vers le fichier CSV
    csv_file_path = os.path.join(data_dir, ratings_csv)

    try:
        # Lire le fichier CSV et retourner un DataFrame Pandas
        data = pd.read_csv(csv_file_path)
        print("Dataset ratings loaded")  # Confirmation du chargement réussi
        return data

    except FileNotFoundError:
        print(f"Erreur : Le fichier '{csv_file_path}' n'a pas été trouvé.")
        raise  # Relancer l'exception pour signaler l'erreur

    except pd.errors.EmptyDataError:
        print(f"Erreur : Le fichier '{csv_file_path}' est vide.")
        raise  # Relancer l'exception pour signaler l'erreur

    except pd.errors.ParserError:
        print(f"Erreur : Impossible d'analyser le fichier '{csv_file_path}'.")
        raise  # Relancer l'exception pour signaler l'erreur

    except Exception as e:
        print(f"Erreur lors du chargement des données : {e}")
        raise  # Relancer l'exception pour signaler l'erreur


def train_SVD_model(df) -> tuple:
    """Entraîne un modèle SVD de recommandation et sauvegarde le modèle.

    Args:
        df (pd.DataFrame): DataFrame contenant les colonnes userId, movieId et bayesian_mean.
    """

    start_time = datetime.now()  # Démarrer la mesure du temps

    # Préparer les données pour Surprise
    reader = Reader(rating_scale=(0.5, 5))
    data = Dataset.load_from_df(df[['userId', 'movieId', 'bayesian_mean']], reader=reader)

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

     # Définir le chemin vers le dossier 'models' pour enregistrer le modèle entraîné
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, "..", "..", "models")

    directory = os.path.join(output_dir, 'model_SVD.pkl')

    with open(directory, 'wb') as file:
        pickle.dump(model, file)
        print(f'Modèle sauvegardé sous {directory}')

    end_time = datetime.now()  # Fin de la mesure du temps

    # Calculer et afficher la durée totale de l'entraînement
    duration = end_time - start_time
    print(f'Durée de l\'entraînement : {duration}')


def create_X(df):
    """Crée une matrice creuse et les dictionnaires de correspondance.

    Args:
        df (pd.DataFrame): DataFrame avec colonnes userId, movieId, rating.

    Returns:
        tuple: (matrice_creuse, user_mapper, movie_mapper, user_inv_mapper, movie_inv_mapper)
    """
    M = df['userId'].nunique()
    N = df['movieId'].nunique()

    user_mapper = dict(zip(np.unique(df["userId"]), list(range(M))))
    movie_mapper = dict(zip(np.unique(df["movieId"]), list(range(N))))

    user_inv_mapper = dict(zip(list(range(M)), np.unique(df["userId"])))
    movie_inv_mapper = dict(zip(list(range(N)), np.unique(df["movieId"])))

    user_index = [user_mapper[i] for i in df['userId']]
    item_index = [movie_mapper[i] for i in df['movieId']]

    X = csr_matrix((df["rating"], (user_index,item_index)), shape=(M,N))

    return X, user_mapper, movie_mapper, user_inv_mapper, movie_inv_mapper


def train_matrix_model(df, k = 10, metric='cosine'):
    """Entraîne et sauvegarde un modèle KNN basé sur une matrice creuse.

    Args:
        df (pd.DataFrame): DataFrame avec les données d'évaluation.
        k (int): Nombre de voisins à considérer.
        metric (str): Métrique de distance pour KNN.
    """
    # Démarrer la mesure du temps
    start_time = datetime.now()
    X, user_mapper, movie_mapper, user_inv_mapper, movie_inv_mapper = create_X(df)
    # Transposer la matrice X pour que les films soient en lignes et les utilisateurs en colonnes
    X = X.T
    # Initialiser NearestNeighbors avec k+1 car nous voulons inclure le film lui-même dans les voisins
    kNN = NearestNeighbors(n_neighbors=k + 1, algorithm="brute", metric=metric)

    kNN.fit(X)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, "..", "..", "models")

    directory = os.path.join(output_dir, 'model_KNN.pkl')

    with open(directory, 'wb') as file:
        pickle.dump(kNN, file)
        print(f'Modèle KNN sauvegardé sous {directory}')

    end_time = datetime.now()  # Fin de la mesure du temps

    # Calculer et afficher la durée totale de l'entraînement
    duration = end_time - start_time
    print(f'Durée de l\'entraînement : {duration}')

if __name__ == "__main__":
    ratings = read_ratings('processed_ratings.csv')
    print('Entrainement du modèle SVD')
    train_SVD_model(ratings)
    print('Entrainement du modèle CSR Matrix')
    train_matrix_model(ratings)