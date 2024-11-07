from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime


def process_scraping():
    # TODO: Implémenter le traitement des features
    pass


with DAG(
    "scraping_missing_data",
    tags=["project", "data", "scraping"],
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
) as dag:

    build_features_task = PythonOperator(
        task_id="build_features", python_callable=process_scraping
    )
