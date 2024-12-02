from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.kubernetes.secret import Secret
from kubernetes.client import models as k8s

secret_database = Secret(
  deploy_type="env",
  deploy_target="DATABASE",
  secret="sql-conn",
)

secret_user = Secret(
  deploy_type="env",
  deploy_target="USER",
  secret="sql-conn",
)

secret_password = Secret(
  deploy_type="env",
  deploy_target="PASSWORD",
  secret="sql-conn",
)

with DAG(
  dag_id='load_transform_save_db',
  tags=['antoine'],
  default_args={
    'owner': 'airflow',
    'start_date': days_ago(0, minute=1),
    },
  schedule_interval=None,  # Pas de planification automatique,
  catchup=False
) as dag:

    python_transform = KubernetesPodOperator(
    task_id="python_transform",
    image="antoinepela/projet_reco_movies:order-python-transform-latest",
    cmds=["/bin/bash", "-c", "/app/start.sh"],
    namespace= "airflow",
    )

python_transform