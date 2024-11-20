import pytest
from airflow.models import DagBag
import sys
import os
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../airflow/dags')))
from predict_knn_model import create_X, my_dag

def test_dag_loaded():
    """Test que le DAG est correctement chargé."""
    assert my_dag is not None
    assert len(my_dag.tasks) == 1
    assert my_dag.task_dict['train_model'] is not None


    # Test des propriétés basiques du DAG
    assert my_dag.dag_id == 'KNN_train_model'
    assert my_dag.schedule_interval == '@daily'
    assert my_dag.default_args['owner'] == 'airflow'


def test_create_X():
    # Créer un petit DataFrame de test
    test_data = pd.DataFrame({
        'userId': [1, 1, 2, 2],
        'movieId': [1, 2, 1, 2],
        'rating': [4.0, 3.5, 5.0, 4.0]
    })

    # Tester la fonction create_X
    X = create_X(test_data)
    assert X.shape == (2, 2)