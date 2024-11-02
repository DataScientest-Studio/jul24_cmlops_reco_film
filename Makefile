.PHONY: help setup1 setup2 setup-light start stop restart logs-supabase logs-airflow logs-api clean network

# Help command to list all available targets
help:
	@echo "Usage: make [target]"
	@echo "Targets:"
	@echo "  setup1      	- Setup environment, load initial data and set .env files based on .env.example"
	@echo "  setup2      	- Build all services and load data"
	@echo "  setup-light 	- Build features and all services without loading data"
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
	python3 -m venv .venv
	source .venv/bin/activate
	pip install -r requirements-dev.txt
	@echo "###### DATA & MODEL ######"
	python ml/src/data/import_raw_data.py
	python ml/src/features/build_features.py 
	python ml/src/models/train_model.py
	@echo "###### ENV VARIABLES #####"
	cd supabase/docker && cp .env.example .env
	cd airflow && cp .env.example .env
	cp .env.example .env
	@echo "##########################"
	@echo "Set the desired env variables in the .env files (supabase/docker/.env, airflow/.env and .env) then run 'make setup2'"

# Setup: Build all services and load data
setup2: network
	cd supabase/docker && docker compose pull
	cd airflow && echo -e "AIRFLOW_UID=$(id -u)" >> .env && cd ..
	cd airflow && docker compose up airflow-init
	docker compose build
	make clean-db
	@echo "##########################"
	@echo "Run 'make start' to start the services"

# Setup: Build features and all services without loading data
setup-light: network
	python ml/src/features/build_features.py
	cd supabase/docker && cp .env.example .env
	cd supabase/docker && docker compose pull
	cd airflow && cp .env.example .env&& echo -e "AIRFLOW_UID=$(id -u)" >> .env && cd ..
	cd airflow && docker compose up airflow-init
	docker compose build
	@echo "##########################"
	@echo "Run 'make clean-db' to load the data into the database"

# Start: start all services
start: network
	cd supabase/docker && docker compose up -d
	cd airflow && docker compose up -d
	docker compose up -d
	@echo "##########################"
	@echo "supabase: http://localhost:8000"
	@echo "airflow: http://localhost:8080"
	@echo "streamlit: http://localhost:8501"

# Stop: stop all services
stop:
	docker compose stop
	docker compose -f airflow/docker-compose.yaml stop
	docker compose -f supabase/docker/docker-compose.yml stop

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
	docker compose -f supabase/docker/docker-compose.yml down -v
	docker compose -f airflow/docker-compose.yaml down -v
	docker compose down -v
	docker network rm backend || true

# Clean-db: delete all data in the database and reload the schema and data
clean-db: network
	cd supabase/docker && docker compose down -v
	rm -rf supabase/docker/volumes/db/data/
	cd supabase/docker && docker compose up -d
	sleep 5 && python ml/src/data/load_data_in_db.py
	@echo "##########################"
	@echo "Run 'make start' to start all the services"

# Network: create the Docker network 'backend'
network:
	docker network create backend || true
