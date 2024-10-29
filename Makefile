.PHONY: help setup start stop restart logs-supabase logs-airflow logs-api clean network

# Help command to list all available targets
help:
	@echo "Usage: make [target]"
	@echo "Targets:"
	@echo "  setup      	- Setup environment, load initial data and build all services"
	@echo "  start      	- Start all services"
	@echo "  stop       	- Stop all services"
	@echo "  restart    	- Restart all services"
	@echo "  logs-supabase  - Show logs for supabase"
	@echo "  logs-airflow   - Show logs for airflow"
	@echo "  logs-api       - Show logs for api"
	@echo "  clean          - Remove all containers and networks"
	@echo "  clean-db       - Delete all data in the database and reload the schema and data"
	@echo "  network        - Create the Docker network 'backend'"

# Setup: Setup environment, load initial data and build all services
setup:
	@echo "##########################"
	@echo "###### SETUP ENV #########"
	@echo "##########################"
	python3 -m venv .venv
	source .venv/bin/activate
	pip install -r requirements-dev.txt
	@echo "##########################"
	@echo "###### DATA & MODEL ######"
	@echo "##########################"
	python ml/src/data/import_raw_data.py
	python ml/src/data/make_dataset.py
	python ml/src/features/build_features.py
	python ml/src/models/train_model.py
	@echo "##########################"
	@echo "###### BUILD SERVICES ####"
	@echo "##########################"
	docker compose -f supabase/docker/docker-compose.yml pull
	cd airflow && echo -e "AIRFLOW_UID=$(id -u)" > .env && cd ..
	docker compose -f airflow/docker-compose.yaml up airflow-init
	docker compose build
	@echo "##########################"
	@echo "##########################"
	@echo "Run 'make clean-db' to load the data into the database then run 'make start' to start the services"

# Start: start all services
start: network
	cd supabase/docker && docker compose up -d
	cd airflow && docker compose up -d
	docker compose up -d
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

# Logs: show logs for all services
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
	docker compose -f supabase/docker/docker-compose.yml down -v
	rm -rf supabase/docker/volumes/db/data/
	docker compose -f supabase/docker/docker-compose.yml up -d
	python ml/src/data/load_data.py

# Network: create the Docker network 'backend'
network:
	docker network create backend || true
