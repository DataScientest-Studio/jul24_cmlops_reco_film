import streamlit as st
from streamlit.testing import TestRunner
from streamlit.app.utils import display_movies_grid
from streamlit.app.pages import 4_Authentification, 5_Application

def test_display_movies_grid():
    runner = TestRunner()
    movies_info = {
        "0": {"poster_path": "path/to/poster1.jpg", "title": "Movie 1", "vote_average": 8.5},
        "1": {"poster_path": "path/to/poster2.jpg", "title": "Movie 2", "vote_average": 7.3},
        "2": {"poster_path": "path/to/poster3.jpg", "title": "Movie 3", "vote_average": 9.1},
        "3": {"poster_path": "path/to/poster4.jpg", "title": "Movie 4", "vote_average": 6.8},
    }
    runner.run(display_movies_grid, movies_info)
    assert runner.get_widget("markdown").exists()

def test_authentication_page():
    runner = TestRunner()
    runner.run(auth_page)
    assert runner.get_widget("header").exists()

def test_application_page():
    runner = TestRunner()
    runner.run(app_page)
    assert runner.get_widget("markdown").exists()

if __name__ == "__main__":
    test_display_movies_grid()
    test_authentication_page()
    test_application_page()