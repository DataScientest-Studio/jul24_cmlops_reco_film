import pytest
from unittest.mock import patch, MagicMock
from api.auth import validate_username, validate_email, validate_password
import pandas as pd
import numpy as np


@pytest.fixture
def mock_db():
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Simule qu'aucun utilisateur n'existe déjà

    with patch('psycopg2.connect') as mock_connect:
        mock_connect.return_value = mock_conn
        yield mock_connect


@pytest.fixture
def mock_data():

    ratings = pd.DataFrame({
        'userId': [1, 2, 3],
        'movieId': [1, 2, 3],
        'rating': [4.0, 3.5, 5.0]
    })
    movies = pd.DataFrame({
        'movieId': [1, 2, 3],
        'title': ['Movie1', 'Movie2', 'Movie3']
    })
    links = pd.DataFrame({
        'movieId': [1, 2, 3],
        'imdbId': ['0111161', '0068646', '0071562']
    })
    return ratings, movies, links

@pytest.fixture(autouse=True)
def mock_data_loading(mock_data):
    ratings, movies, links = mock_data
    with patch('api.predict.read_ratings', return_value=ratings), \
         patch('api.predict.read_movies', return_value=movies), \
         patch('api.predict.read_links', return_value=links), \
         patch('api.predict.load_model', return_value=MagicMock()), \
         patch('api.predict.create_X', return_value=(MagicMock(), {}, {}, {}, {})):
        yield



@pytest.mark.usefixtures("mock_db")
def test_validate_username():
    # Test pour le nom d'utilisateur valide
    valid_username = "valid_username"
    error_message = validate_username(valid_username)
    assert error_message is None

    # Test pour le nom d'utilisateur invalide
    invalid_username = "@invalidusername"
    error_message = validate_username(invalid_username)
    assert error_message == "Le nom d'utilisateur ne doit contenir que des lettres, chiffres et underscores."

@pytest.mark.usefixtures("mock_db")
def test_validate_email():
    # Test pour l'email valide
    valid_email = "valid@example.com"
    error_message = validate_email(valid_email)
    assert error_message is None

    # Test pour l'email invalide
    invalid_email = "invalid-email"
    error_message = validate_email(invalid_email)
    assert error_message == "L'adresse e-mail n'est pas valide."

@pytest.mark.usefixtures("mock_db")
def test_validate_password():
    # Test pour le mot de passe valide
    valid_password = "StrongPassword123!"
    error_message = validate_password(valid_password)
    assert error_message is None

    # Test pour le mot de passe invalide (trop court)
    invalid_password = "Short1!"
    error_message = validate_password(invalid_password)
    assert error_message == "Le mot de passe doit contenir au moins 12 caractères."