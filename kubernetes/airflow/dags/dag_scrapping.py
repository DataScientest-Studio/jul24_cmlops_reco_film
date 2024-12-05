from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.kubernetes.secret import Secret
from airflow.operators.python import PythonOperator

# Définition des secrets
secret_password = Secret(
    deploy_type="env",
    deploy_target="PASSWORD",
    secret="sql-conn"
)

secret_token = Secret(
    deploy_type="env",
    deploy_target="TMDB_TOKEN",
    secret="sql-conn"
)

# Définition des arguments par défaut
default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),  # Commencer à s'exécuter à partir d'un jour en arrière
}

# Création du DAG principal
with DAG(
    dag_id='scrapping_TMDB_data',
    description='Scraping TMDB data and updating database',
    tags=['antoine'],
    default_args=default_args,
    schedule_interval='@daily',  # Exécution quotidienne à minuit
    catchup=False,
) as dag:

    # Tâche pour exécuter le script de transformation dans un pod Kubernetes
    dag_scraping_and_inserting_movies = KubernetesPodOperator(
        task_id="python_scrapping",
        image="antoinepela/projet_reco_movies:python-scrapping-latest",
        cmds=["python3", "scrapping.py"],
        namespace="airflow",
        env_vars={
            'DATABASE': 'postgres',
            'USER': 'postgres',
        },
        secrets=[secret_password, secret_token],  # Ajout des deux secrets
    )

    # Tâche pour récupérer les genres depuis TMDB
    get_genres_task = PythonOperator(
        task_id='get_genres_task',
        python_callable=genres_request,
        dag=dag,
    )

    # Tâche pour scraper IMDb et récupérer les liens
    scrape_imdb_task = PythonOperator(
        task_id='scrape_imdb_task',
        python_callable=scrape_imdb_first_page,
        dag=dag,
    )

    # Tâche pour récupérer les infos des films depuis TMDB
    scrape_infos_task = PythonOperator(
        task_id='scrape_movies_infos_task',
        python_callable=api_tmdb_request,
        op_kwargs={
            'cleaned_links': '{{ task_instance.xcom_pull(task_ids="scrape_imdb_task") }}',
            'genres': '{{ task_instance.xcom_pull(task_ids="get_genres_task") }}'
        },
        dag=dag,
    )

    # Tâche pour insérer les données dans la base
    insert_data_task = PythonOperator(
        task_id='insert_data_movies_task',
        python_callable=insert_data_movies,
        op_kwargs={
            'api_results': '{{ task_instance.xcom_pull(task_ids="scrape_movies_infos_task") }}',
        },
        dag=dag,
    )

# Définir l'ordre d'exécution des tâches dans le DAG
get_genres_task >> scrape_imdb_task >> scrape_infos_task >> insert_data_task >> dag_scraping_and_inserting_movies