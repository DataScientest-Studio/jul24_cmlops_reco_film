from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime


def train_model():
    # TODO: Implémenter l'entraînement du modèle
    pass


with DAG(
    "training_model",
    tags=["project", "model", "training"],
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily", 
    catchup=False,
) as dag:

    train_task = PythonOperator(
        task_id="train_model",
        python_callable=train_model
    )
