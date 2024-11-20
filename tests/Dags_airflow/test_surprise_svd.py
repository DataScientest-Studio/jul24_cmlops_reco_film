import pytest
from airflow.models import DagBag
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../airflow/dags')))


@pytest.fixture()
def dagbag():
    return DagBag()

def test_dag_loaded(dagbag):
    dag = dagbag.get_dag(dag_id="SVD_train_and_compare_model")
    assert dagbag.import_errors == {}
    assert dag is not None
    assert len(dag.tasks) == 1

