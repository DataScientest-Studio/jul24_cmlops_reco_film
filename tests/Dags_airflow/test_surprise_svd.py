import pytest
import sys
import os
from airflow.models import DagBag
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../airflow/dags')))
from predict_surprise_SVD import svd_dag

def test_dag_loaded():
    """Test que le DAG est correctement chargé."""
    assert svd_dag is not None
    assert len(svd_dag.tasks) == 1
    assert svd_dag.task_dict['train_model'] is not None

    # Test des propriétés basiques du DAG
    assert svd_dag.dag_id == 'SVD_train_and_compare_model'
    assert svd_dag.schedule_interval == '@daily'
    assert svd_dag.default_args['owner'] == 'airflow'
    assert svd_dag.default_args['start_date'] == datetime(2024, 11, 3)

