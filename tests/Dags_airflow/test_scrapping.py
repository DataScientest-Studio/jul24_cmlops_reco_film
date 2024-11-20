import unittest
from airflow.models import DagBag
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../airflow/dags')))
from scrapping import get_db_connection, scrape_imdb

class TestScrapingDAG(unittest.TestCase):
    def setUp(self):
        self.dagbag = DagBag()

    def test_dag_loaded(self):
        dag = self.dagbag.get_dag(dag_id='imdb_scraper_dag')
        self.assertIsNotNone(dag)
        self.assertEqual(len(dag.tasks), 3)

    def test_db_connection(self):
        try:
            next(get_db_connection())
            connection_successful = True
        except Exception:
            connection_successful = False
        self.assertTrue(connection_successful)

    def test_dependencies(self):
        dag = self.dagbag.get_dag(dag_id='imdb_scraper_dag')
        update_movies_task = dag.get_task('update_movies_task')
        update_links_task = dag.get_task('update_links_task')

        self.assertLess(
            dag.get_task('scrape_imdb_task').downstream_task_ids,
            update_movies_task.downstream_task_ids
        )

if __name__ == '__main__':
    unittest.main()