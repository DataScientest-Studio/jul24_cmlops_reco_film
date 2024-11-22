.PHONY: help setup1 setup2 start stop down restart logs-supabase logs-airflow logs-api clean network

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

# Logs: show logs for supabase, airflow and api
logs-supabase:
	docker compose -f supabase/docker/docker-compose.yml logs -f

logs-airflow:
	docker compose -f airflow/docker-compose.yaml logs -f

logs-api:
	docker compose logs -f

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

# Network: create the Docker network 'backend'
network:
	docker network create backend || true

# TODO: add targets for testing
