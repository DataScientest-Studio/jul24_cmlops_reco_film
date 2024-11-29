.PHONY: help setup1 setup2 start stop restart clean network

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
	@echo "  clean          - Remove all containers and networks"
	@echo "  clean-db       - Delete all data in the database and reload the schema and data"
	@echo "  network        - Create the Docker network 'backend'"

# Setup: Setup environment, load initial data and set env files based on .env.example	
setup1:
	@echo "###### SETUP ENV #########"
	python3 -m venv .venv
	.venv/bin/pip install -r requirements-dev.txt
	@echo "###### DATA & MODEL ######"
	.venv/bin/python ml/src/data/import_raw_data.py
	.venv/bin/python ml/src/features/build_features.py 
	.venv/bin/python ml/src/models/train_model.py
	@echo "###### ENV VARIABLES #####"
	cd supabase && cp .env.example .env
	cd airflow && cp .env.example .env
	cd airflow && echo "AIRFLOW_UID=$(shell id -u)" >> .env
	cp .env.example .env
	@echo "##########################"
	@echo "Set the desired env variables in the .env files (supabase/.env, airflow/.env and .env) then run 'make setup2'"

# Setup: Build all services and load data
setup2: network
	cd supabase && docker compose pull
	cd airflow && docker compose up airflow-init
	docker compose build
	cd supabase && docker compose up -d
	sleep 10 && python ml/src/data/load_data_in_db.py
	@echo "##########################"
	@echo "Run 'make start' to start the services"

# Start: start all services
start: network
	mkdir -p mlflow/db_data mlflow/minio_data
	cd supabase && docker compose up -d
	cd airflow && docker compose up -d
	docker compose up -d
	@echo "##########################"
	@echo "supabase: http://localhost:8000"
	@echo "airflow: http://localhost:8080"
	@echo "streamlit: http://localhost:8501"
	@echo "mlflow: http://localhost:5001"
	@echo "minio: http://localhost:9001"
	@echo "prometheus: http://localhost:9090"
	@echo "grafana: http://localhost:3000"

# Stop: stop all services
stop:
	docker compose stop
	docker compose -f airflow/docker-compose.yaml stop
	cd supabase && docker compose stop

# Restart: restart all services
restart: stop start

# Clean: stop and remove all containers, networks, and volumes for all services
clean:
	cd supabase && docker compose down -v --remove-orphans
	cd airflow && docker compose down -v --remove-orphans
	docker compose down -v --remove-orphans
	docker network rm backend || true
	rm -rf supabase/volumes/db/data/
	rm -rf supabase/volumes/storage/
	rm -rf mlflow/minio_data/
	rm -rf mlflow/db_data/

# Clean-db: delete all data in the database and reload the schema and data
clean-db: network
	cd supabase && docker compose down -v
	rm -rf supabase/volumes/db/data/
	rm -rf supabase/volumes/storage/
	cd supabase && docker compose up -d
	sleep 10 && python ml/src/data/load_data_in_db.py
	@echo "##########################"
	@echo "Run 'make start' to start all the services"

# Network: create the Docker network 'backend'
network:
	docker network create backend || true

# TODO: add targets for testing, logs, etc.
