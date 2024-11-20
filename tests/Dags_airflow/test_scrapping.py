import pytest
from airflow.models import DagBag
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../airflow/dags')))
from scrapping import dag

def test_dag_loaded():
    """Test que le DAG est correctement chargé."""
    assert dag is not None
    assert len(imdb_scraper_dag.tasks) == 3
    assert dag.task_dict['scrape_imdb_task'] is not None
    assert dag.task_dict['update_movies_task'] is not None
    assert dag.task_dict['update_links_task'] is not None


    # Test des propriétés basiques du DAG
    assert dag.dag_id == 'imdb_scraper_dag'
    assert dag.schedule_interval == '@daily'
    assert dag.default_args['owner'] == 'airflow'
    assert dag.default_args['start_date'] == datetime(2024, 11, 19)