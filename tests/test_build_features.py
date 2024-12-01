import unittest
import pandas as pd
import importlib.util
import sys
import os

# Définir le chemin du fichier à tester
module_file_path = '/home/antoine/jul24_cmlops_reco_film/kubernetes/airflow/order/docker/prod/python_transform/build_features.py'

# Charger le module
spec = importlib.util.spec_from_file_location("build_features", module_file_path)
build_features = importlib.util.module_from_spec(spec)
sys.modules["build_features"] = build_features
spec.loader.exec_module(build_features)



class TestDataProcessing(unittest.TestCase):

    def setUp(self):
        self.raw_data_relative_path = "app/data/to_ingest/bronze"
        self.data_directory = "app/data/to_ingest/silver"

    def test_download_and_save_file(self):
        url = "https://mlops-project-db.s3.eu-west-1.amazonaws.com/movie_recommandation/"
        build_features.download_and_save_file(url, self.raw_data_relative_path)
        self.assertTrue(os.path.exists(os.path.join(self.raw_data_relative_path, 'ratings.csv')))
        self.assertTrue(os.path.exists(os.path.join(self.raw_data_relative_path, 'movies.csv')))
        self.assertTrue(os.path.exists(os.path.join(self.raw_data_relative_path, 'links.csv')))

    def test_load_data(self):
        dfs = build_features.load_data(self.raw_data_relative_path)
        self.assertIsInstance(dfs[0], pd.DataFrame)  # Vérifie que c'est un DataFrame
        self.assertIsInstance(dfs[1], pd.DataFrame)  # Vérifie que c'est un DataFrame
        self.assertIsInstance(dfs[2], pd.DataFrame)  # Vérifie que c'est un DataFrame

    def test_create_users(self):
        users_df = build_features.create_users()
        self.assertEqual(len(users_df), 500)  # Vérifie que 500 utilisateurs sont créés

if __name__ == "__main__":
    unittest.main()