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
	cp .env.example .env
	echo "AIRFLOW_UID=$(shell id -u)" >> .env
	@echo "##########################"
	@echo "Set the desired env variables in the .env file then run 'make setup2'"

# Setup: Build all services and load data
setup2: network
	cd supabase && docker compose pull
	cd supabase && docker compose --env-file ../.env up -d
	cd airflow && docker compose --env-file ../.env up airflow-init
	cd mlflow && docker compose --env-file ../.env build
	cd monitoring && docker compose --env-file ../.env build
	cd app && docker compose --env-file ../.env build
	sleep 10 && python ml/src/data/load_data_in_db.py
	@echo "##########################"
	@echo "Run 'make start' to start the services"

# Start: start all services
start: network
	mkdir -p mlflow/db_data mlflow/minio_data
	cd supabase && docker compose --env-file ../.env up -d
	cd mlflow && docker compose --env-file ../.env up -d
	cd airflow && docker compose --env-file ../.env up -d
	cd app && docker compose --env-file ../.env up -d
	cd monitoring && docker compose --env-file ../.env up -d
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
	cd app && docker compose --env-file ../.env stop
	cd airflow && docker compose --env-file ../.env stop
	cd supabase && docker compose --env-file ../.env stop
	cd monitoring && docker compose --env-file ../.env stop
	cd mlflow && docker compose --env-file ../.env stop

# Restart: restart all services
restart: stop start

# Clean: stop and remove all containers, networks, and volumes for all services
clean:
	cd supabase && docker compose --env-file ../.env down -v --rmi all --remove-orphans
	cd airflow && docker compose --env-file ../.env down -v --rmi all --remove-orphans
	cd app && docker compose --env-file ../.env down -v --rmi all --remove-orphans
	cd mlflow && docker compose --env-file ../.env down -v --rmi all --remove-orphans
	cd monitoring && docker compose --env-file ../.env down -v --rmi all --remove-orphans
	docker network rm backend || true
	docker builder prune -f
	rm -rf supabase/volumes/db/data/
	rm -rf supabase/volumes/storage/
	rm -rf mlflow/minio_data/
	rm -rf mlflow/db_data/
	rm -rf airflow/logs/*

# Very-clean: stop and remove all containers, networks, and volumes for all services, and remove all images
# Warning: this will remove all images, not just the ones for the current project
very-clean:
	docker system prune -a -f --volumes

# Clean-db: delete all data in the database and reload the schema and data
clean-db: network
	cd supabase && docker compose --env-file ../.env down -v
	rm -rf supabase/volumes/db/data/
	rm -rf supabase/volumes/storage/
	cd supabase && docker compose --env-file ../.env up -d --build
	sleep 10 && python ml/src/data/load_data_in_db.py
	@echo "##########################"
	@echo "Run 'make start' to start all the services"

# Network: create the Docker network 'backend'
network:
	docker network create backend || true

# TODO: add targets for testing, logs, etc.
