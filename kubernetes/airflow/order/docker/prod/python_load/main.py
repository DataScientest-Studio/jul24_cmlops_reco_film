import os
import psycopg2
import pandas as pd
from sqlalchemy import create_engine, table, column
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime
import json

# Définition des tables SQLAlchemy pour les opérations d'upsert
table_movies = table('movies',
    column('movieId'),
    column('title'),
    column('genres'),
    column('year')
)

table_ratings = table('ratings',
    column('id'),
    column('userId'),
    column('movieId'),
    column('rating'),
    column('timestamp'),
    column('bayesian_mean')
)

table_links = table('links',
    column('id'),
    column('movieId'),
    column('imdbId'),
    column('tmdbId')
)

table_users = table('users',
    column('userId'),
    column('username'),
    column('email'),
    column('hached_password')
)

def load_config():
    """Charge la configuration de la base de données à partir des variables d'environnement."""
    config = {}
    config['host'] = os.getenv('AIRFLOW_POSTGRESQL_SERVICE_HOST')
    config['database'] = os.getenv('DATABASE')
    config['user'] = os.getenv('USER')
    config['password'] = os.getenv('PASSWORD')
    return config

def connect(config):
    """Connecte au serveur PostgreSQL."""
    try:
        with psycopg2.connect(**config) as conn:
            print('Connected to the PostgreSQL server.')
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)

def execute_query_psql(query, config):
    """Exécute une requête SQL pour insérer des données dans une table."""
    conn_string = 'postgresql://' + config['user'] + ':' + config['password'] + '@' + config['host'] + '/' + config['database']
    try:
        db = create_engine(conn_string)
        with db.begin() as conn:
            res = conn.execute(query)
            return res.rowcount  # Retourne le nombre de lignes affectées par la requête
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

def upsert_movies_to_psql(table_movies, df_movies):
    """Insère ou met à jour des enregistrements dans la table movies."""
    dict_customer = [{k: v if pd.notnull(v) else None for k, v in m.items()} for m in df_movies.to_dict(orient='records')]

    # Création de l'instruction d'insertion avec gestion des conflits
    insert_stmt = insert(table_movies).values(dict_customer)

    do_update_stmt = insert_stmt.on_conflict_do_update(
        index_elements=[table_movies.c.movieId],
        set_={
            'movieId': insert_stmt.excluded.movieId,
            'title': insert_stmt.excluded.title,
            'genres': insert_stmt.excluded.genres,
            'year': insert_stmt.excluded.year,
        }
    )

    rowcount = execute_query_psql(do_update_stmt, config)
    print(f'{rowcount} movies rows has been inserted or updated')

def upsert_ratings_to_psql(table_ratings, df_ratings):
    """Insère ou met à jour des enregistrements dans la table ratings."""
    dict_product = [{k: v if pd.notnull(v) else None for k, v in m.items()} for m in df_ratings.to_dict(orient='records')]

    insert_stmt = insert(table_ratings).values(dict_product)

    do_update_stmt = insert_stmt.on_conflict_do_update(
        index_elements=[table_ratings.c.id],
        set_={
            'id': insert_stmt.excluded.id,
            'userId': insert_stmt.excluded.userId,
            'movieId': insert_stmt.excluded.movieId,
            'rating': insert_stmt.excluded.rating,
            'timestamp': insert_stmt.excluded.timestamp,
            'bayesian_mean': insert_stmt.excluded.bayesian_mean
        }
    )

    rowcount = execute_query_psql(do_update_stmt, config)
    print(f'{rowcount} ratings rows has been inserted or updated')

def upsert_links_to_psql(table_links, df_links):
    """Insère ou met à jour des enregistrements dans la table links."""
    dict_product = [{k: v if pd.notnull(v) else None for k, v in m.items()} for m in df_links.to_dict(orient='records')]

    insert_stmt = insert(table_links).values(dict_product)

    do_update_stmt = insert_stmt.on_conflict_do_update(
        index_elements=[table_links.c.id],  # Correction ici : utiliser table_links au lieu de table_ratings
        set_={
            'id': insert_stmt.excluded.id,
            'movieId': insert_stmt.excluded.movieId,
            'imdbId': insert_stmt.excluded.imdbId,
            'tmdbId': insert_stmt.excluded.tmdbId
        }
    )

    rowcount = execute_query_psql(do_update_stmt, config)
    print(f'{rowcount} links rows has been inserted or updated')

def upsert_users_to_psql(table_users, df_users):
   """Insère ou met à jour des enregistrements dans la table users."""
   dict_product = [{k: v if pd.notnull(v) else None for k, v in m.items()} for m in df_users.to_dict(orient='records')]

   insert_stmt = insert(table_users).values(dict_product)

   do_update_stmt = insert_stmt.on_conflict_do_update(
       index_elements=[table_users.c.userId],
       set_={
           'userId': insert_stmt.excluded.userId,
           'username': insert_stmt.excluded.username,  # Correction ici : utiliser username au lieu de movieId
           'email': insert_stmt.excluded.email,
           'hached_password': insert_stmt.excluded.hached_password  # Correction ici : utiliser hached_password au lieu de tmdbId
       }
   )

   rowcount = execute_query_psql(do_update_stmt, config)
   print(f'{rowcount} users rows has been inserted or updated')


if __name__ == '__main__':
   data_directory = 'data'
   config = load_config()
   print(os.environ)
   print(config)
   df_ratings = pd.read_csv(f'{data_directory}/to_ingest/silver/processed_ratings.csv')
   upsert_ratings_to_psql(table_ratings, df_ratings)
   df_movies = pd.read_csv(f'{data_directory}/to_ingest/silver/processed_movies.csv')
   upsert_movies_to_psql(table_movies, df_movies)
   df_links = pd.read_csv(f'{data_directory}/to_ingest/silver/processed_links.csv')
   upsert_links_to_psql(table_links, df_links)
   df_users = pd.read_csv(f'{data_directory}/to_ingest/silver/users.csv')
   upsert_users_to_psql(table_users, df_users)