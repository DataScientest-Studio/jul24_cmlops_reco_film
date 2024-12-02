from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python_operator import PythonOperator
from airflow import settings
from airflow.models.connection import Connection
from airflow.operators.postgres_operator import PostgresOperator
import os

conn_keys = ['conn_id', 'conn_type', 'host', 'login', 'password', 'schema']

def get_postgres_conn_conf():
    postgres_conn_conf = {}
    postgres_conn_conf['host'] = os.getenv("AIRFLOW_POSTGRESQL_SERVICE_HOST")
    postgres_conn_conf['port'] = os.getenv("AIRFLOW_POSTGRESQL_SERVICE_PORT")
    if (postgres_conn_conf['host'] == None):
        raise TypeError("The AIRFLOW_POSTGRESQL_SERVICE_HOST isn't defined")
    elif (postgres_conn_conf['port'] == None):
        raise TypeError("The AIRFLOW_POSTGRESQL_SERVICE_PORT isn't defined")
    postgres_conn_conf['conn_id'] = 'postgres'
    postgres_conn_conf['conn_type'] = 'postgres'
    postgres_conn_conf['login'] = 'postgres'
    postgres_conn_conf['password'] = 'postgres'
    postgres_conn_conf['schema'] = 'postgres'
    return postgres_conn_conf

def create_conn(**kwargs):
    session = settings.Session()
    print("Session created")
    connections = session.query(Connection)
    print("Connections listed")
    if not kwargs['conn_id'] in [connection.conn_id for connection in connections]:
        conn_params = { key: kwargs[key] for key in conn_keys }
        conn = Connection(**conn_params)
        session.add(conn)
        session.commit()
        print("Connection Created")
    else:
        print("Connection already exists")
    session.close()

postgres_conn_conf = get_postgres_conn_conf()

with DAG(
    dag_id='init_order',
    tags=['order', 'antoine'],
    default_args={
        'owner': 'airflow',
        'start_date': days_ago(0, minute=1),
    },
    catchup=False
) as dag:

    create_postgres_conn = PythonOperator(
        task_id='create_postgres_conn',
        python_callable=create_conn,
        op_kwargs=postgres_conn_conf
    )

    create_tables = PostgresOperator(
    task_id='create_tables',
    postgres_conn_id='postgres',
    sql="""
    CREATE TABLE IF NOT EXISTS movies (
        movieId SERIAL PRIMARY KEY,
        title VARCHAR(200) NOT NULL,
        genres TEXT,
        year INT
    );

    CREATE TABLE IF NOT EXISTS ratings (
        id SERIAL PRIMARY KEY,
        userId INT,
        movieId INT REFERENCES movies(movieId),
        rating FLOAT NOT NULL,
        timestamp INT,
        bayesian_mean FLOAT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS links (
        id SERIAL PRIMARY KEY,
        movieId INT REFERENCES movies(movieId),
        imdbId INT,
        tmdbId INT
    );

    CREATE TABLE IF NOT EXISTS users (
        userId SERIAL PRIMARY KEY,
        username VARCHAR(50) NOT NULL,
        email VARCHAR(100) NOT NULL UNIQUE,
        hached_password VARCHAR(300) NOT NULL
    );
    """
)

create_postgres_conn >> create_tables
