import streamlit as st
from streamlit.testing.v1 import AppTest

def test_display_movies_grid():
    at = AppTest.from_file("utils.py")

    movies_info = {
        "0": {"poster_path": "path/to/poster1.jpg", "title": "Movie 1", "vote_average": 8.5},
        "1": {"poster_path": "path/to/poster2.jpg", "title": "Movie 2", "vote_average": 7.3},
        "2": {"poster_path": "path/to/poster3.jpg", "title": "Movie 3", "vote_average": 9.1},
        "3": {"poster_path": "path/to/poster4.jpg", "title": "Movie 4", "vote_average": 6.8},
    }

    at.run(movies_info)
    # Vérifier que les colonnes sont créées
    assert len(at.get_columns()) == 4

    # Vérifier que chaque film est affiché
    markdown_elements = at.get_markdown()
    assert len(markdown_elements) == 4

    # Vérifier le contenu pour chaque film
    for i, movie in enumerate(movies_info.values()):
        assert movie["title"] in markdown_elements[i].value
        assert str(movie["vote_average"]) in markdown_elements[i].value

    # Vérifier que les images sont affichées
    images = at.get_images()
    assert len(images) == 4

if __name__ == "__main__":
    test_display_movies_grid()
