# Movie Recommendation MLOps Project

This project is a starting pack for MLOps projects focused on the subject of "movie recommendation". It provides a structured framework to develop, train, and deploy machine learning models for recommending movies to users. It uses Supabase for the backend, Airflow for the orchestration, MLflow for the tracking, Minio for the storage of the models, Prometheus and Grafana for the monitoring.

## Project Organization

The project is organized as follows:

```
├── .github
│   └── workflows
│       └── test-api.yml                    <- GitHub Actions workflow for testing the API.
│
├── airflow
│   ├── Dockerfile
│   ├── dags
│   │   ├── scraping_new_movies.py          <- DAG for scraping new movies.
│   │   └── train_model_dag.py              <- DAG for training the model.
│   ├── docker-compose.override.yaml
│   ├── docker-compose.yaml
│   ├── logs
│   └── requirements.txt
│
├── api
│   └── predict
│       ├── Dockerfile
│       ├── main.py                         <- Main file for the API.
│       ├── metrics.py                      <- Metrics for the API.
│       └── requirements.txt                <- Requirements for the API.
│
├── ml
│   ├── models
│   │   └── model.pkl                       <- Initial trained model.
│   └── src
│       ├── data
│       │   ├── check_structure.py          <- Script for checking the structure of the data.
│       │   ├── import_raw_data.py          <- Script for importing raw data.
│       │   └── load_data_in_db.py          <- Script for loading data into the database.
│       ├── features
│       │   └── build_features.py           <- Script for building features.
│       ├── models
│       │   ├── predict_model.py            <- Script for making predictions.
│       │   └── train_model.py              <- Script for training the model.
│       └── requirements.txt                <- Requirements for the project.
│
├── mlflow
│   ├── Dockerfile
│   └── requirements.txt
│
├── monitoring
│   ├── grafana
│   │   └── provisioning
│   │       ├── dashboards
│   │       │   ├── api_dashboard.json      <- Dashboard for the API.
│   │       │   └── dashboards.yml          <- Dashboards configuration.
│   │       └── datasources
│   │           └── datasource.yml          <- Datasource configuration.
│   └── prometheus
│       └── prometheus.yml                  <- Prometheus configuration.
│
├── streamlit
│   └── pages
│   │   ├── 1_Recommandations.py            <- Page for recommendations.
│   │   └── 2_Profil.py                     <- Page for the profile.
│   ├── Dockerfile
│   ├── Home.py                             <- Main page.
│   ├── requirements.txt                    <- Requirements for the Streamlit app.
│   ├── style.css                           <- CSS for the pages.
│   ├── supabase_auth.py                    <- Supabase authentication.
│   └── utils.py                            <- Utility functions.
│

├── supabase
│   ├── README.md
│   ├── docker-compose.override.yml
│   ├── docker-compose.s3.yml
│   ├── docker-compose.yml
│   └── volumes
│       ├── api
│       │   └── kong.yml
│       ├── db
│       │   ├── _supabase.sql
│       │   ├── init
│       │   │   ├── 01-project-tables.sql    <- SQL script for creating project tables.
│       │   │   ├── 02-auth-trigger.sql      <- SQL script for creating the auth trigger.
│       │   │   ├── 03-security-policies.sql <- SQL script for creating security policies.
│       │   │   └── data.sql
│       │   ├── jwt.sql
│       │   ├── logs.sql
│       │   ├── pooler.sql
│       │   ├── realtime.sql
│       │   ├── roles.sql
│       │   └── webhooks.sql
│       ├── functions
│       │   ├── hello
│       │   │   └── index.ts
│       │   └── main
│       │       └── index.ts
│       ├── logs
│       │   └── vector.yml
│       └── pooler
│           └── pooler.exs
│
├── tests
│   ├── requirements.txt                    <- Requirements for the tests.
│   ├── test_api_predict.py                 <- Test for the API.
│   └── test_rls.py                         <- Test for the RLS.
│
├── .env.example                            <- Example of the .env file.
├── .gitignore                              <- Git ignore file.
├── docker-compose.yml                      <- Docker compose file.
├── LICENSE
├── Makefile                                <- Makefile for the project.
├── README.md                               <- This README file.
├── requirements-dev.txt
└── requirements-ref.txt
```

## Tools Used

- **Python**: The main programming language used for data processing, model training, and prediction.
- **Docker & Docker Compose**: Used for containerizing the application and setting up a local development environment.
- **Supabase**: A backend service for managing the database and authentication.
- **MLflow**: For tracking experiments and managing machine learning models.
- **Apache Airflow**: For orchestrating data workflows and model training pipelines.
- **Streamlit**: For building interactive web applications to display recommendations.
- **FastAPI**: For building the REST API for the movie recommendation service.
- **Prometheus**: For monitoring and alerting.
- **Grafana**: For visualizing metrics.

## Before setting up the project

Make sure you have the following tools installed:
- Docker
   ```bash
   docker --version
   ```
- Docker Compose
   ```bash
   docker compose version
   ```
- Python 3.10+
   ```bash
   python --version
   ```
- pip
   ```bash
   pip --version
   ```
- git
   ```bash
   git --version
   ```
- make
   ```bash
   make --version
   ```

## Setting Up the Project for Local Development

To set up the project for local development, from the root of the repository follow the steps below:

1. Run the `make setup1` command.

2. Set the environment variable TMDB_API_TOKEN in the .env file. This is necessary to be able to execute the DAG `scraping_new_movies.py` in Airflow.

3. Run the `make setup2` command.

4. Run the `make start` command.

5. Setup access and the bucket for MLFlow:
   - From your browser, go to `localhost:9001` to access the MinIO console. Sign in using the root user and password specified in the `.env` file.
   - Once you sign in, navigate to the Access Keys tab and click the Create access key button. This will take you to the Create Access Key page.
   - Your access key and secret key are not saved until you click the Create button. Do not navigate away from this page until this is done. Don’t worry about copying the keys from this screen. Once you click the Create button, you will be given the option to download the keys to your file system (in a JSON file).
   - Next, create a bucket named `mlflow`. This is straightforward, go into the Buckets tab and click the `Create Bucket` button.
   - Once you have your keys and you have created your bucket, you can finish setting up the services by stopping the containers, updating the `.env`, and then restarting the containers. The command below will stop and remove your containers.
     ```bash
     cd mlflow
     docker compose down
     docker compose --env-file ../.env up -d --build
     ```
     (may be useful to do it in a new terminal to avoid cache issues with the `.env` file)

**Access the Services**:
- Supabase: [http://localhost:8000](http://localhost:8000)
- Airflow: [http://localhost:8080](http://localhost:8080)
- Streamlit: [http://localhost:8501](http://localhost:8501)
- API: [http://localhost:8002/docs](http://localhost:8002/docs)
- MLFlow: [http://localhost:5001](http://localhost:5001)
- MinIO: [http://localhost:9001](http://localhost:9001)
- Prometheus: [http://localhost:9090](http://localhost:9090)
- Grafana: [http://localhost:3000](http://localhost:3000)
