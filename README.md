(base) antoine@AntoineASUS:~/Ml_Ops_Movies_Reco$ tree
.
├── LICENSE
├── README.md
├── app
│   ├── docker-compose.yml
│   ├── fastapi
│   │   ├── Dockerfile
│   │   ├── app
│   │   │   ├── README.md
│   │   │   ├── __init__.py
│   │   │   ├── __pycache__
│   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   ├── auth.cpython-312.pyc
│   │   │   │   ├── database.cpython-312.pyc
│   │   │   │   ├── main.cpython-312.pyc
│   │   │   │   ├── models.cpython-312.pyc
│   │   │   │   └── predict.cpython-312.pyc
│   │   │   ├── auth.py
│   │   │   ├── database.py
│   │   │   ├── main.py
│   │   │   ├── model
│   │   │   ├── models.py
│   │   │   ├── predict.py
│   │   │   ├── raw
│   │   │   └── user_db
│   │   └── requirements.txt
│   ├── model-trainer-predictor
│   │   ├── Dockerfile
│   │   ├── app
│   │   │   ├── app
│   │   │   │   └── model
│   │   │   └── predict_knn_model.py
│   │   └── requirements.txt
│   ├── prometheus
│   │   └── prometheus.yml
│   ├── shared_volume
│   │   ├── logs
│   │   │   ├── grafana
│   │   │   └── prometheus
│   │   ├── model
│   │   │   └── model_knn.pkl
│   │   ├── mongodb_data
│   │   │   ├── WiredTiger
│   │   │   ├── WiredTiger.lock
│   │   │   ├── WiredTiger.turtle
│   │   │   ├── WiredTiger.wt
│   │   │   ├── WiredTigerHS.wt
│   │   │   ├── _mdb_catalog.wt
│   │   │   ├── collection-0-1509500977226906948.wt
│   │   │   ├── collection-0-7603690427217424249.wt
│   │   │   ├── collection-2-1509500977226906948.wt
│   │   │   ├── collection-2-7603690427217424249.wt
│   │   │   ├── collection-4-1509500977226906948.wt
│   │   │   ├── collection-4-7603690427217424249.wt
│   │   │   ├── collection-7-1509500977226906948.wt
│   │   │   ├── diagnostic.data  [error opening dir]
│   │   │   ├── index-1-1509500977226906948.wt
│   │   │   ├── index-1-7603690427217424249.wt
│   │   │   ├── index-3-1509500977226906948.wt
│   │   │   ├── index-3-7603690427217424249.wt
│   │   │   ├── index-5-1509500977226906948.wt
│   │   │   ├── index-5-7603690427217424249.wt
│   │   │   ├── index-6-1509500977226906948.wt
│   │   │   ├── index-8-1509500977226906948.wt
│   │   │   ├── index-9-1509500977226906948.wt
│   │   │   ├── journal  [error opening dir]
│   │   │   ├── mongod.lock
│   │   │   ├── mongodb_data
│   │   │   ├── sizeStorer.wt
│   │   │   └── storage.bson
│   │   ├── raw
│   │   │   ├── links2.csv
│   │   │   ├── movies.csv
│   │   │   └── ratings.csv
│   │   └── user_db
│   │       └── movies_app_users.db
│   └── streamlit
│       ├── Dockerfile
│       ├── app
│       │   ├── __init__.py
│       │   ├── __pycache__
│       │   │   └── streamlit_app.cpython-312.pyc
│       │   ├── app.py
│       │   ├── images
│       │   │   ├── datascientest.png
│       │   │   └── netflix-catalogue.jpg
│       │   └── pages
│       │       ├── 1_💬_Contexte & Objectifs.py
│       │       ├── 2_💹_Choix_Modèle.py
│       │       ├── 3_💾_Gestion BDD.py
│       │       ├── 4_🔐_Authentification.py
│       │       ├── 5_📽️_Application.py
│       │       ├── 6_🔍_new_user.py
│       │       ├── 7_🔭_ids_users.py
│       │       └── 8_📡_Monitoring.py
│       └── requirements.txt
├── grafana_backup.db
├── models
│   └── model.pkl
├── notebooks
│   ├── 1_exploration_data.ipynb
│   ├── 2_Nettoyage des données.ipynb
│   ├── 3_models_cross_validation.ipynb
│   ├── 4_Gridsearch_SVD.ipynb
│   ├── 4_train_svd_model.ipynb
│   ├── import_data_mongodb.ipynb
│   ├── scrapping_cover.ipynb
│   ├── tensorflow_predict.ipynb
│   ├── test.ipynb
│   └── test_cover.ipynb
├── references
├── reports
│   └── figures
├── requirements.txt
├── setup.py
└── src
    ├── __init__.py
    ├── config
    ├── data
    │   ├── __init__.py
    │   ├── __pycache__
    │   │   └── check_structure.cpython-312.pyc
    │   ├── check_structure.py
    │   ├── data
    │   │   └── raw
    │   │       ├── README.txt
    │   │       ├── genome-scores.csv
    │   │       ├── genome-tags.csv
    │   │       ├── links.csv
    │   │       ├── movies.csv
    │   │       ├── ratings.csv
    │   │       └── tags.csv
    │   ├── import_raw_data.py
    │   └── make_dataset.py
    ├── features
    │   ├── __init__.py
    │   ├── build_features.py
    │   └── build_features_surprise.py
    ├── models
    │   ├── __init__.py
    │   ├── predict_model.py
    │   ├── train_knn_model.py
    │   ├── train_model.py
    │   └── train_svd_model.py
    └── visualization
        ├── __init__.py
        └── visualize.py
