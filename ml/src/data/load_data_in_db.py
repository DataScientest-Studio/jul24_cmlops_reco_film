import pandas as pd
import os
from supabase import create_client, Client
from tqdm import tqdm
import numpy as np
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

def connect_to_supabase() -> Client:
    """
    Établit une connexion à Supabase en utilisant les variables d'environnement.

    Returns:
        Client: Une instance du client Supabase.

    Raises:
        ValueError: Si les variables d'environnement SUPABASE_URL ou SUPABASE_KEY ne sont pas définies.
    """
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")

    if not all([supabase_url, supabase_key]):
        raise ValueError(
            "Les variables d'environnement SUPABASE_URL et SUPABASE_KEY doivent être définies."
        )

    # S'assurer que l'URL commence par http:// ou https://
    supabase_url = (
        f"https://{supabase_url}"
        if not supabase_url.startswith(("http://", "https://"))
        else supabase_url
    )

    return create_client(supabase_url, supabase_key)

def initialize_supabase_connection() -> Client:
    """
    Initialise la connexion à Supabase et gère les erreurs potentielles.

    Returns:
        Client: Une instance du client Supabase.
    """
    try:
        return connect_to_supabase()
    except ValueError as ve:
        print(f"Erreur lors de la connexion à Supabase : {ve}")
    except Exception as e:
        print(
            f"Une erreur inattendue s'est produite lors de la connexion à Supabase : {e}"
        )
    exit(1)

def load_data(csv_path: str, table_name: str, supabase: Client, expected_types: dict, dtype=None):
    """
    Charge les données d'un fichier CSV dans une table Supabase.

    Args:
        csv_path (str): Chemin vers le fichier CSV à charger.
        table_name (str): Nom de la table dans Supabase.
        supabase (Client): Instance du client Supabase.
        expected_types (dict): Types attendus pour les colonnes de la table.
        dtype (dict, optional): Dictionnaire des types de données pour pandas. Par défaut, None.
    """
    # Si aucun type n'est spécifié, utiliser les types attendus
    if dtype is None:
        dtype = expected_types

    # Modifier les types pour permettre les valeurs NA dans les colonnes d'entiers
    for col, typ in dtype.items():
        if typ == "int64":
            dtype[col] = "Int64"  # Utiliser le type nullable Int64 de pandas

    # Lire le nombre total de lignes dans le fichier CSV
    total_rows = len(pd.read_csv(csv_path))

    # Définir la taille des chunks pour le chargement par morceaux
    chunksize = 5000
    total_chunks = (total_rows // chunksize) + (1 if total_rows % chunksize != 0 else 0)

    # Charger le fichier CSV par morceaux et insérer dans Supabase
    for chunk in tqdm(
        pd.read_csv(csv_path, dtype=dtype, chunksize=chunksize),
        desc=f"Insertion des {total_rows} lignes de {table_name}",
        total=total_chunks,
        dynamic_ncols=True,
    ):
        # Remplacer les valeurs manquantes par None
        chunk = chunk.where(pd.notnull(chunk), None)

        # Convertir le DataFrame en liste de dictionnaires pour l'insertion
        data = chunk.to_dict(orient="records")

        # Préparer les données pour l'insertion en gérant les types
        data = [
            {
                k: (
                    float(v) if isinstance(v, (float, np.float64)) and not pd.isna(v)
                    else (v if not pd.isna(v) else None)
                )
                for k, v in record.items()
            }
            for record in data
        ]

        # Insérer ou mettre à jour les données dans Supabase
        supabase.table(table_name).upsert(data).execute()

# Initialiser la connexion à Supabase
supabase = initialize_supabase_connection()

# Définir le chemin vers le dossier contenant les données brutes
base_dir = os.path.dirname(os.path.abspath(__file__))
# Construire le chemin vers le répertoire contenant les données traitées
data_dir = os.path.join(base_dir, '..', '..', 'data', 'processed')

# Configuration des chemins des fichiers et des types attendus pour chaque table
data_config = {
    "tables": {
        "movies": os.path.join(data_dir, "processed_movies.csv"),
        "links": os.path.join(data_dir, "processed_links.csv"),
        "ratings": os.path.join(data_dir, "processed_ratings.csv"),
        "users": os.path.join(data_dir, "users.csv")
    },
    "expected_types": {
        "movies": {
            "movieId": "int64",
            "title": "object",
            "genres": "object",
            "year": "int64"
        },
        "ratings": {
            "userId": "int64",
            "movieId": "int64",
            "rating": "float64",
            "timestamp": "int64",
            "bayesian_mean": "float64"
        },
        "links": {
            "movieId": "int64",
            "imdbId": "object",
            "tmdbId": "object"
        },
        "users": {
            "userId": "int64",
            "email": "object",
            "password": "object"
        },
    },
}

#  Charger les données pour chaque table configurée
for table_name, file_path in data_config["tables"].items():
    if table_name in data_config["expected_types"]:
        load_data(
            file_path,
            table_name,
            supabase,
            data_config["expected_types"][table_name]
        )
    else:
        load_data(file_path, table_name, supabase, {})

print("Données chargées avec succès dans la base de données Supabase.")