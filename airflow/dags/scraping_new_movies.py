from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime


def scrape_new_movies():
    # TODO: Implémenter le scraping des nouveaux films
    pass


with DAG(
    "scraping_new_movies",
    tags=["project", "data", "scraping"],
    start_date=datetime(2024, 1, 1), 
    schedule_interval="@daily",
    catchup=False,
) as dag:

    scrape_task = PythonOperator(
        task_id="scrape_new_movies",
        python_callable=scrape_new_movies
    )
