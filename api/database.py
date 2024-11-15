import psycopg2
from dotenv import load_dotenv
import os
from contextlib import contextmanager

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

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
    username=os.getenv("POSTGRES_USER")
    password=os.getenv("POSTGRES_PASSWORD")
    database=os.getenv("POSTGRES_DB")
    host=os.getenv("POSTGRES_HOST")
    port=os.getenv("POSTGRES_PORT")
    conn = None
    try:
        conn = psycopg2.connect(
            database=database,
            host=host,
            user=username,
            password=password,
            port=port
        )
        print("Connection à la base de données OK")
        yield conn
    except psycopg2.Error as e:
        print(f"Erreur lors de la connexion à la base de données: {e}")
        raise
    finally:
        if conn is not None:
            conn.close()
            print("Connexion à la base de données fermée")


