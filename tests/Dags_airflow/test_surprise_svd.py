import unittest
from airflow.models import DagBag
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../airflow/dags')))
from predict_surprise_SVD import read_ratings

class TestSVDModelDAG(unittest.TestCase):
    def setUp(self):
        self.dagbag = DagBag()

    def test_dag_loaded(self):
        dag = self.dagbag.get_dag(dag_id='SVD_train_and_compare_model')
        self.assertIsNotNone(dag)
        self.assertEqual(len(dag.tasks), 1)

    def test_read_ratings(self):
        try:
            df = read_ratings('processed_ratings.csv')
            self.assertTrue('userId' in df.columns)
            self.assertTrue('movieId' in df.columns)
            self.assertTrue('rating' in df.columns)
        except Exception as e:
            self.fail(f"read_ratings a échoué avec l'erreur: {str(e)}")

if __name__ == '__main__':
    unittest.main()