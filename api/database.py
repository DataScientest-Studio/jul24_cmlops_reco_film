import psycopg2
from dotenv import load_dotenv
from contextlib import contextmanager
import os

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

POSTGRES_USER= os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD= os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB= os.getenv('POSTGRES_DB')
POSTGRES_HOST= os.getenv('POSTGRES_HOST')
POSTGRES_PORT= os.getenv('POSTGRES_PORT')

@contextmanager
def get_db_connection():
    """
    Gestionnaire de contexte pour la connexion à la base de données.
    Ouvre une connexion et la ferme automatiquement après utilisation.

    Utilisation:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM table")
    """
    conn = None
    try:
        conn = psycopg2.connect(
            database=POSTGRES_DB,
            host=POSTGRES_HOST,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            port=POSTGRES_PORT
        )
        print("Connection à la base de données OK")
        yield conn
    except psycopg2.Error as e:
        print(f"Erreur lors de la connexion à la base de données: {e}")
        conn.rollback()
        raise
    finally:
        if conn is not None:
            conn.close()
            print("Connexion à la base de données fermée")


