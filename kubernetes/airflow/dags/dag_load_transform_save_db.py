from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.kubernetes.secret import Secret

secret_password  = Secret(
  deploy_type="env",
  deploy_target="PASSWORD",
  secret="sql-conn"
)

with DAG(
  dag_id='load_transform_save_db',
  tags=['antoine'],
  default_args={
    'owner': 'airflow',
    'start_date': days_ago(0, minute=1),
    },
  catchup=False
) as dag:

    python_transform = KubernetesPodOperator(
    task_id="python_transform",
    image="antoinepela/projet_reco_movies:python-transform-latest",
    cmds=["/bin/bash", "-c", "/app/start.sh"],
    namespace= "airflow",
    env_vars={
            'DATABASE': 'postgres',
            'USER': 'postgres',
        },
    secrets= [secret_password],
    )


python_transform