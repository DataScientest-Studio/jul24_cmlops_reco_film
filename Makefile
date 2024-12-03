NAMESPACE1 = reco-movies
NAMESPACE2 = airflow
NAMESPACE3 = mlflow

.PHONY: help setup1 setup2 start stop down restart logs-supabase logs-airflow logs-api logs-fastapi clean network all namespace pv secrets configmaps deployments services ingress clean-kube-reco clean-kube-airflow apply-configmap start-minikube start-airflow pv-airflow reco start-mlflow

# Help command to list all available targets
help:
	@echo "Usage: make [target]"
	@echo "Targets:"
	@echo "  setup1      	- Setup environment, load initial data and set .env files based on .env.example"
	@echo "  setup2      	- Build all services and load data"
	@echo "  start      	- Start all services"
	@echo "  stop       	- Stop all services"
	@echo "  restart    	- Restart all services"
	@echo "  logs-supabase  - Show logs for supabase"
	@echo "  logs-airflow   - Show logs for airflow"
	@echo "  logs-api       - Show logs for api"
	@echo "  logs-fastapi   - Show logs for FastAPI"
	@echo "  clean          - Remove all containers and networks"
	@echo "  clean-db       - Delete all data in the database and reload the schema and data"
	@echo "  network        - apply the Docker network 'backend'"

# Setup: Setup environment, load initial data and set env files based on .env.example
# TODO: gérer le fait que l'on ait pas les posterUrl a ce stade pour le build des features
setup1:
	@echo "###### SETUP ENV #########"
	# python3 -m venv .venv
	# source .venv/bin/activate
	pip install -r requirements-dev.txt
	@echo "###### DATA & MODEL ######"
	@echo 'Chargement des données'
	python ml/src/data/import_raw_data.py
	@echo 'Création des features'
	python ml/src/features/build_features.py
	@echo 'Entrainement des modèles SVD & KNN'
	python ml/src/models/train_model.py
	@echo "###### ENV VARIABLES #####"
	cd postgres && cp .env.example .env
	cd airflow && cp .env.example .env
	cp .env.example .env
	@echo "##########################"
	@echo "Set the desired env variables in the .env files (postgres/.env, airflow/.env and .env) then run 'make setup2'"

# Setup: Build all services and load data
setup2: network
	cd postgres && docker compose up --build --no-start
	docker compose up --build --no-start
	cd airflow && echo "AIRFLOW_UID=$(shell id -u)" >> .env
	cd airflow && docker compose up --build --no-start
	@echo "##########################"
	@echo "Run 'make start' to start the services"

# Start: start all services
start: network
	cd postgres && docker compose up -d
	./wait-for-it.sh 0.0.0.0:5432 --timeout=60 --strict -- echo "Database is up"
	docker compose up -d
	cd airflow && docker compose up -d
	@echo "##########################"
	@echo "Pg Admin: http://localhost:5050"
	@echo "Airflow: http://127.0.0.1:8081"
	@echo "Streamlit: http://localhost:8501"
	@echo "FastAPI: http://localhost:8002/docs"
	@echo "Grafana: http://localhost:3000"
	@echo "MlFlow: http://localhost:5000"

# Stop: stop all services
stop:
	docker compose stop
	docker compose -f airflow/docker-compose.yaml stop
	docker compose -f postgres/docker-compose.yml stop

down:
	docker compose down --volumes --remove-orphans
	docker compose -f airflow/docker-compose.yaml down --volumes --remove-orphans
	docker compose -f postgres/docker-compose.yml down --volumes --remove-orphans

# Restart: restart all services
restart: stop start


logs-airflow:
	docker compose -f airflow/docker-compose.yaml logs -f

logs-api:
	docker compose logs -f

logs-fastapi:
	docker compose logs -f fastapi

# Clean: stop and remove all containers, networks, and volumes for all services
clean:
	cd supabase/docker && docker compose down -v
	cd airflow && docker compose down -v
	docker compose down -v
	docker network rm backend || true
	bash clean_docker.sh

# Clean-db: delete all data in the database and reload the schema and data
clean-db: network
	cd supabase/docker && docker compose down -v
	rm -rf supabase/docker/volumes/db/data/
	cd supabase/docker && docker compose up -d
	sleep 10 && python ml/src/data/load_data_in_db.py
	@echo "##########################"
	@echo "Run 'make start' to start all the services"

# Network: apply the Docker network 'backend'
network:
	docker network apply backend || true



###### MAKEFILE KUBERNETES
all: namespace install-airflow pv-airflow pv secrets configmaps deployments services ingress

start-minikube:
	minikube start --driver=docker --memory=8192 --cpus=4 --mount --mount-string= "/home/antoine/jul24_cmlops_reco_film/:/host"

install-helm:
	curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
	chmod 700 get_helm.sh
	./get_helm.sh

# Installation de helm Airflow
start-airflow:
	sudo apt-get update
	helm repo add apache-airflow https://airflow.apache.org
	helm upgrade --install airflow apache-airflow/airflow --namespace airflow --create-namespace -f kubernetes/airflow/my_airflow_values.yml
	kubectl apply -f kubernetes/persistent-volumes/airflow-local-dags-folder-pv.yml
	kubectl apply -f kubernetes/persistent-volumes/airflow-local-dags-folder-pvc.yml
	kubectl apply -f kubernetes/persistent-volumes/airflow-local-logs-folder-pv.yml
	kubectl apply -f kubernetes/persistent-volumes/airflow-local-logs-folder-pvc.yml
	kubectl apply -f kubernetes/persistent-volumes/mlfow-storage-pv.yml
	kubectl apply -f kubernetes/persistent-volumes/mlfow-storage-pvc.yml
	kubectl apply -f kubernetes/secrets/airflow-secrets.yaml
	kubectl apply -f kubernetes/configmaps/airflow-configmaps.yml
	kubectl apply -f kubernetes/deployments/pgadmin-deployment.yml
	kubectl apply -f kubernetes/services/pgadmin-service.yml

start-mlflow:
	helm repo add bitnami https://charts.bitnami.com/bitnami
	helm repo update
	helm install mlf-ts bitnami/mlflow --namespace mlflow --create-namespace
	kubectl apply -f kubernetes/services/mlflow-service.yml


delete-pv-airflow:
	kubectl delete pv airflow-local-dags-folder || true
	kubectl delete pv airflow-local-logs-folder || true


# Vérifie si kubectl est connecté à un cluster
check-kube:
	@kubectl cluster-info > /dev/null 2>&1 || { echo "kubectl n'est pas connecté à un cluster"; exit 1; }

reco: namespace pv secrets configmaps deployments services ingress


namespace: check-kube
	kubectl apply -f kubernetes/namespace/namespace.yml --validate=false

pv: check-kube
	kubectl apply -f kubernetes/persistent-volumes/fastapi-persistent-volume.yml --validate=false
	kubectl apply -f kubernetes/persistent-volumes/grafana-persistent-volume.yml --validate=false
	kubectl apply -f kubernetes/persistent-volumes/minio-persistent-volumes.yml --validate=false
	kubectl apply -f kubernetes/persistent-volumes/postgres-api-persistent-volumes.yml --validate=false
	kubectl apply -f kubernetes/persistent-volumes/prometheus-persistent-volume.yml --validate=false
	kubectl apply -f kubernetes/persistent-volumes/pgadmin-persistent-volume.yml --validate=false

secrets: check-kube
	kubectl apply -f kubernetes/secrets/secrets.yml --validate=false

configmaps: check-kube
	kubectl apply -f kubernetes/configmaps/configmaps.yml --validate=false

deployments: check-kube
	kubectl apply -f kubernetes/deployments/postgres-api-deployment.yml --validate=false
	kubectl apply -f kubernetes/deployments/postgres-mlflow-deployment.yml --validate=false
	kubectl apply -f kubernetes/deployments/mlflow-deployment.yml --validate=false
	kubectl apply -f kubernetes/deployments/fastapi-deployment.yml --validate=false
	kubectl apply -f kubernetes/deployments/streamlit-deployment.yml --validate=false
	kubectl apply -f kubernetes/deployments/prometheus-deployment.yml --validate=false
	kubectl apply -f kubernetes/deployments/grafana-deployment.yml --validate=false
	kubectl apply -f kubernetes/deployments/node-exporter-deployment.yml --validate=false
	kubectl apply -f kubernetes/deployments/minio-deployment.yml --validate=false
	kubectl apply -f kubernetes/deployments/postgres-exporter-deployment.yml --validate=false
	kubectl apply -f kubernetes/deployments/pgadmin-deployment.yml --validate=false

services: check-kube
	kubectl apply -f kubernetes/services/services.yml

ingress: check-kube
	kubectl apply -f kubernetes/ingress/ingress.yml

clean-kube-reco: check-kube
	kubectl delete namespace $(NAMESPACE1)

clean-kube-airflow: check-kube
	kubectl delete namespace $(NAMESPACE2)


clean-kube-mlflow: check-kube
	kubectl delete namespace $(NAMESPACE3)