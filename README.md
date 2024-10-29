# Project Name

This project is a starting Pack for MLOps projects based on the subject "movie_recommandation". It's not perfect so feel free to make some modifications on it.

## Project Organization

    ├── LICENSE
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── logs               <- Logs from training and predicting
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   ├── check_structure.py
    │   │   ├── import_raw_data.py
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   ├── visualization  <- Scripts to create exploratory and results oriented visualizations
    │   │   └── visualize.py
    │   └── config         <- Describe the parameters used in train_model.py and predict_model.py

---

jul24_cmlops_reco_film/

├── app # Dossier principal pour l'application
│ ├── api # API pour les services de données et de prédiction
│ │ ├── data # Service API pour l'accès aux données
│ │ │ ├── Dockerfile # Configuration Docker pour le service de données
│ │ │ ├── main.py # Point d'entrée principal pour l'API de données
│ │ │ ├── requirements.txt # Dépendances pour le service de données
│ │ │ └── start.sh # Script de démarrage pour le service de données
│ │ └── predict # Service API pour les prédictions
│ │ ├── Dockerfile # Configuration Docker pour le service de prédiction
│ │ ├── main.py # Point d'entrée principal pour l'API de prédiction
│ │ └── requirements.txt # Dépendances pour le service de prédiction
│ ├── database # Configuration de la base de données
│ │ ├── Dockerfile # Configuration Docker pour la base de données
│ │ └── init_db.sh # Script d'initialisation de la base de données
│ └── streamlit # Interface utilisateur Streamlit
│ ├── Dockerfile # Configuration Docker pour l'application Streamlit
│ ├── app.py # Application Streamlit principale
│ ├── requirements.txt # Dépendances pour l'application Streamlit
│ └── style.css # Styles CSS pour l'interface Streamlit
├── ml # Pipeline de machine learning
│ ├── data # Données pour le modèle ML
│ │ ├── processed # Données traitées
│ │ │ ├── movie_matrix.csv # Matrice des films traitée
│ │ │ └── user_matrix.csv # Matrice des utilisateurs traitée
│ │ └── raw # Données brutes
│ │ ├── README.txt # Description des données brutes
│ │ ├── genome-scores.csv # Scores du génome de tags
│ │ ├── genome-tags.csv # Tags du génome
│ │ ├── links.csv # Liens vers d'autres sources de données de films
│ │ ├── movies.csv # Informations sur les films
│ │ ├── ratings.csv # Évaluations des utilisateurs
│ │ └── tags.csv # Tags attribués par les utilisateurs
│ ├── models # Modèles entraînés
│ │ └── model.pkl # Modèle sérialisé
│ ├── notebooks # Notebooks Jupyter pour l'exploration et l'analyse
│ │ ├── test.ipynb # Notebook de test
│ │ └── test_mikhael.ipynb # Notebook de test de Mikhael
│ └── src # Code source du pipeline ML
│ ├── config # Configuration du pipeline ML
│ ├── data # Scripts de traitement des données
│ │ ├── **init**.py # Initialisation du module de données
│ │ ├── check_structure.py # Vérification de la structure des données
│ │ ├── import_raw_data.py # Importation des données brutes
│ │ ├── load_data_in_db.py # Chargement des données dans la base de données
│ │ └── make_dataset.py # Création du jeu de données final
│ ├── features # Scripts de création de features
│ │ ├── **init**.py # Initialisation du module de features
│ │ └── build_features.py # Construction des features
│ ├── models # Scripts pour l'entraînement et la prédiction
│ │ ├── **init**.py # Initialisation du module de modèles
│ │ ├── predict_model.py # Prédiction avec le modèle
│ │ └── train_model.py # Entraînement du modèle
│ ├── visualization # Scripts de visualisation
│ │ ├── **init**.py # Initialisation du module de visualisation
│ │ └── visualize.py # Création de visualisations
│ └── requirements.txt # Dépendances pour le pipeline ML
├── docker-compose.yml # Configuration Docker Compose pour l'ensemble du projet
├── requirements-dev.txt # Dépendances de développement
├── requirements-ref.txt # Dépendances de référence
├── LICENSE # Licence du projet
└── README.md # Documentation principale du projet

24 directories, 58 files

## Steps to follow

Convention : All python scripts must be run from the root specifying the relative file path.

### 1- Create a virtual environment using Virtualenv.

    `python -m venv my_env`

### Activate it

    `./my_env/Scripts/activate`

### Install the packages from requirements.txt (You can ignore the warning with "setup.py")

    `pip install -r .\requirements.txt`

### 2- Execute import_raw_data.py to import the 4 datasets (say yes when it asks you to create a new folder)

    `python .\src\data\import_raw_data.py`

### 3- Execute make_dataset.py initializing `./data/raw` as input file path and `./data/processed` as output file path.

    `python .\src\data\make_dataset.py`

### 4- Execute build_features.py to preprocess the data (this can take a while)

    `python .\src\features\build_features.py`

### 5- Execute train_model.py to train the model

    `python .\src\models\train_model.py`

### 5- Finally, execute predict_model.py file to make the predictions (by default you will be printed predictions for the first 5 users of the dataset).

    `python .\src\models\predict_model.py`

### Note that we have 10 recommandations per user

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
