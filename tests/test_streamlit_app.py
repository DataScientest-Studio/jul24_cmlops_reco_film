import pytest
from streamlit.app.utils import display_movies_grid

@pytest.fixture
def sample_movies_info():
    return {
        "0": {"poster_path": "path/to/poster1.jpg", "title": "Movie 1", "vote_average": 8.5},
        "1": {"poster_path": "path/to/poster2.jpg", "title": "Movie 2", "vote_average": 7.3},
        "2": {"poster_path": "path/to/poster3.jpg", "title": "Movie 3", "vote_average": 9.1},
        "3": {"poster_path": "path/to/poster4.jpg", "title": "Movie 4", "vote_average": 6.8},
    }

def test_display_movies_grid(sample_movies_info):
    # Appeler la fonction et capturer le résultat
    result = display_movies_grid(sample_movies_info)

    # Vérifier que le résultat contient les informations attendues
    assert isinstance(result, dict) or isinstance(result, list), "Le résultat devrait être un dict ou une liste"

    # Vérifier que tous les films sont présents
    for movie_id, movie_info in sample_movies_info.items():
        # Adapter ces assertions en fonction de la structure de retour réelle de votre fonction
        assert movie_info["title"] in str(result), f"Le titre {movie_info['title']} devrait être présent"
        assert str(movie_info["vote_average"]) in str(result), f"La note {movie_info['vote_average']} devrait être présente"
        assert movie_info["poster_path"] in str(result), f"Le chemin du poster devrait être présent"
