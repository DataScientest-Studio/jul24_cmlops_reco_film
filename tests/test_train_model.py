
import os
import pandas as pd
import numpy as np
import pytest
from ml.src.models.train_model import read_ratings, train_SVD_model, create_X, train_matrix_model

@pytest.fixture
def sample_ratings_df():
    """Crée un DataFrame de test avec des données fictives."""
    return pd.DataFrame({
        'userId': [1, 1, 2, 2, 3],
        'movieId': [1, 2, 1, 3, 2],
        'rating': [4.0, 3.5, 5.0, 2.0, 4.0],
        'bayesian_mean': [4.0, 3.5, 5.0, 2.0, 4.0]
    })

def test_read_ratings_file_not_found():
    """Teste si une exception est levée quand le fichier n'existe pas."""
    with pytest.raises(FileNotFoundError):
        read_ratings('fichier_inexistant.csv')

def test_create_X(sample_ratings_df):
    """Teste la création de la matrice creuse et des mappeurs."""
    X, user_mapper, movie_mapper, user_inv_mapper, movie_inv_mapper = create_X(sample_ratings_df)

    # Vérifier les dimensions de la matrice
    assert X.shape == (3, 3)  # 3 utilisateurs, 3 films

    # Vérifier les mappeurs
    assert len(user_mapper) == 3
    assert len(movie_mapper) == 3
    assert len(user_inv_mapper) == 3
    assert len(movie_inv_mapper) == 3

def test_train_SVD_model(sample_ratings_df, tmp_path):
    """Teste l'entraînement du modèle SVD."""
    # Créer un répertoire temporaire pour le modèle
    os.makedirs(tmp_path / "models", exist_ok=True)

    # Entraîner le modèle
    train_SVD_model(sample_ratings_df)

    # Vérifier si le fichier du modèle a été créé
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "..", "..", "models", "model_SVD.pkl")
    assert os.path.exists(model_path)

def test_train_matrix_model(sample_ratings_df, tmp_path):
    """Teste l'entraînement du modèle KNN."""
    # Créer un répertoire temporaire pour le modèle
    os.makedirs(tmp_path / "models", exist_ok=True)

    # Entraîner le modèle
    train_matrix_model(sample_ratings_df, k=2)

    # Vérifier si le fichier du modèle a été créé
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "..", "..", "models", "model_KNN.pkl")
    assert os.path.exists(model_path)

def test_empty_dataframe():
    """Teste le comportement avec un DataFrame vide."""
    empty_df = pd.DataFrame(columns=['userId', 'movieId', 'rating', 'bayesian_mean'])
    with pytest.raises(ValueError):
        create_X(empty_df)

if __name__ == '__main__':
    pytest.main([__file__])