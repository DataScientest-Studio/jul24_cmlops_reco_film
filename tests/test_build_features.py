
import pytest
import pandas as pd
import numpy as np
import os
from ml.src.features.build_features import (
    bayesienne_mean,
    preprocessing_ratings,
    preprocessing_movies,
    preprocessing_links
)

@pytest.fixture
def sample_ratings_df():
    return pd.DataFrame({
        'userId': [1, 1, 2, 2],
        'movieId': [1, 2, 1, 2],
        'rating': [4.0, 3.0, 5.0, 4.0],
        'timestamp': [1000000, 1000001, 1000002, 1000003]
    })

@pytest.fixture
def sample_movies_df():
    return pd.DataFrame({
        'movieId': [1, 2],
        'title': ['Movie 1 (2020)', 'Movie 2 (2019)'],
        'genres': ['Action|Adventure', 'Comedy|Drama']
    })

@pytest.fixture
def sample_links_df():
    return pd.DataFrame({
        'movieId': [1, 2],
        'imdbId': [111, 222],
        'tmdbId': [123.0, np.nan]
    })

def test_bayesienne_mean():
    series = pd.Series([4.0, 3.0, 5.0])
    M = 4.0  # moyenne globale
    C = 3.0  # nombre moyen de votes
    result = bayesienne_mean(series, M, C)
    assert isinstance(result, float)
    assert 3.0 <= result <= 5.0

def test_preprocessing_ratings(sample_ratings_df, tmp_path):
    # Créer un fichier temporaire pour les tests
    temp_file = tmp_path / "ratings.csv"
    sample_ratings_df.to_csv(temp_file, index=False)

    # Tester la fonction
    result = preprocessing_ratings(str(temp_file))

    assert isinstance(result, pd.DataFrame)
    assert 'bayesian_mean' in result.columns
    assert len(result) == len(sample_ratings_df)

def test_preprocessing_movies(sample_movies_df, tmp_path):
    # Créer un fichier temporaire pour les tests
    temp_file = tmp_path / "movies.csv"
    sample_movies_df.to_csv(temp_file, index=False)

    # Tester la fonction
    result = preprocessing_movies(str(temp_file))

    assert isinstance(result, pd.DataFrame)
    assert 'year' in result.columns
    assert result['genres'].iloc[0] == 'Action, Adventure'
    assert result['year'].iloc[0] == '2020'

def test_preprocessing_links(sample_links_df, tmp_path):
    # Créer un fichier temporaire pour les tests
    temp_file = tmp_path / "links.csv"
    sample_links_df.to_csv(temp_file, index=False)

    # Tester la fonction
    result = preprocessing_links(str(temp_file))

    assert isinstance(result, pd.DataFrame)
    assert result['tmdbId'].dtype == 'int64'
    assert result['tmdbId'].iloc[1] == 0  # Vérifier que la valeur NaN a été remplacée par 0