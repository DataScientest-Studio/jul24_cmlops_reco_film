import unittest
from airflow.models import DagBag
import sys
import os
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../dags')))
from predict_knn_model import read_ratings, create_X

class TestKNNModelDAG(unittest.TestCase):
    def setUp(self):
        self.dagbag = DagBag()

    def test_dag_loaded(self):
        dag = self.dagbag.get_dag(dag_id='KNN_train_model')
        self.assertIsNotNone(dag)
        self.assertEqual(len(dag.tasks), 1)

    def test_create_X(self):
        # Créer un petit DataFrame de test
        test_data = pd.DataFrame({
            'userId': [1, 1, 2, 2],
            'movieId': [1, 2, 1, 2],
            'rating': [4.0, 3.5, 5.0, 4.0]
        })

        # Tester la fonction create_X
        X = create_X(test_data)
        self.assertEqual(X.shape, (2, 2))  # 2 utilisateurs, 2 films

if __name__ == '__main__':
    unittest.main()