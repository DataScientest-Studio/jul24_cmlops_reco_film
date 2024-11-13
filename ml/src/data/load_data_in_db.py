import pandas as pd
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

base_dir = os.path.dirname(os.path.abspath(__file__))
print("base_dir", base_dir)
# Construire le chemin vers le répertoire contenant les données traitées
env_dir = os.path.join(base_dir, '..', '..', '..', 'postgres')
print("env_dir", env_dir )

# Charger les variables d'environnement depuis le fichier .env
load_dotenv(env_dir)

# Configuration de la base de données
DB_NAME = os.getenv('POSTGRES_DB')
DB_USER = os.getenv('POSTGRES_USER')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')
DB_HOST = os.getenv('POSTGRES_HOST')
DB_PORT = os.getenv('POSTGRES_PORT')

def import_csv_to_db(csv_file, table_name):
    """Importe un fichier CSV dans une table PostgreSQL en utilisant pandas."""
    try:
        # Créer le moteur SQLAlchemy
        engine = create_engine(f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

        # Utilisation de pandas pour lire le fichier CSV
        df = pd.read_csv(csv_file)

         # Nettoyage des données : remplacer 'None' par None
        df.replace('None', None, inplace=True)

        # Vérification des types de données et conversion si nécessaire
        df = df.convert_dtypes()  # Convertit les colonnes à des types appropriés

        # Importation des données dans la table PostgreSQL
        df.to_sql(table_name, engine, if_exists='append', index=False)

        print(f"Importation réussie pour {csv_file} dans la table {table_name}.")

    except Exception as e:
        print(f"Erreur lors de l'importation de {csv_file}: {e}")

if __name__ == "__main__":
    # Dictionnaire des fichiers CSV et des tables correspondantes
    # data_dir = os.path.join(base_dir, "..", "..", "data", "processed")
    # users_dir = os.path.join(data_dir, 'users.csv')
    # movies_dir = os.path.join(data_dir, 'processed_movies.csv')
    # ratings_dir = os.path.join(data_dir, 'processed_ratings.csv')
    # links_dir = os.path.join(data_dir, 'processed_links.csv')
    csv_files = {
        "/home/antoine/jul24_cmlops_reco_film/ml/data/processed/users.csv" : 'users',
        "/home/antoine/jul24_cmlops_reco_film/ml/data/processed/processed_movies.csv": 'movies',
        "/home/antoine/jul24_cmlops_reco_film/ml/data/processed/processed_ratings.csv" : 'ratings',
        "/home/antoine/jul24_cmlops_reco_film/ml/data/processed/processed_links.csv" : 'links'
    }

    for csv_file, table_name in csv_files.items():
        if os.path.exists(csv_file):
            import_csv_to_db(csv_file, table_name)
        else:
            print(f"Le fichier {csv_file} n'existe pas.")