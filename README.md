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

## Setting Up for Local Development

To set up the project for local development, follow these steps (every command is as you would execute it in the root of the repository):

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv .venv
   ```

3. **Activate the Virtual Environment**:
   - On Windows:
     ```bash
     .\.venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```

4. **Install Required Packages**:
   ```bash
   pip install -r requirements-dev.txt
   ```

5. **Run the Application**:
   - Execute the data import and processing scripts:
     ```bash
     python ml/src/data/import_raw_data.py
     python ml/src/features/build_features.py
     ```

6. **Train the Model**:
   ```bash
   python ml/src/models/train_model.py
   ```

7. **Set the Environment Variables**:
   - Copy the .env.example file to .env and set the desired variables.
   - In the airflow folder, copy the .env.example file to .env and set the desired variables. The AIRFLOW_UID variable is set like this:
     ```bash
     AIRFLOW_UID=$(id -u) >> .env
     ```
   - In the supabase folder, copy the .env.example file to .env and set the desired variables.

> 💡 **Alternatively**: For a simplified setup, you can run the `make setup1` command which will automatically execute steps 1 through 7. Then set the environment variables as explained above.

The following steps are executed in the root of the repository and require the environment variables to be set in .env files (see step 7).

8. **Create the Docker network**:
   ```bash
   docker network create backend
   ```

9. **Build and Up the Supabase services and load the data in the database**:
   - Pull Supabase images:
     ```bash
     cd supabase && docker compose pull
     ```
   - Up Supabase services:
     ```bash
     cd supabase && docker compose up -d
     ```
   - Load data in the database (make sure the database is ready, it may take a minute):
     ```bash
     python ml/src/data/load_data_in_db.py
     ``` 

10. **Build and Up the Airflow services**:
   - Initialize Airflow:
     ```bash
     cd airflow && docker compose up airflow-init
     ```
   - Up Airflow services:
     ```bash
     cd airflow && docker compose up -d
     ```

11. **Build and Up the other services (API, Streamlit, MLflow + Minio + db, Prometheus, Grafana)**:
   - Build the services:
     ```bash
     docker compose build
     ```
   - Up the services:
     ```bash
     docker compose up -d
     ```

> 💡 **Alternatively**: For a simplified setup, you can run the `make setup2` command followed by the `make start` command which will automatically execute steps 8 through 11.


**Access the Services**:
- Supabase: [http://localhost:8000](http://localhost:8000)
- Airflow: [http://localhost:8080](http://localhost:8080)
- Streamlit: [http://localhost:8501](http://localhost:8501)
- MLflow: [http://localhost:5001](http://localhost:5001)
- Minio: [http://localhost:9001](http://localhost:9001)
- Prometheus: [http://localhost:9090](http://localhost:9090)
- Grafana: [http://localhost:3000](http://localhost:3000)


## TODO
- [ ] parler du docker compose override
- [ ] parler de github actions
- [ ] parler des tests
- [ ] parler du endpoint /reload_model
