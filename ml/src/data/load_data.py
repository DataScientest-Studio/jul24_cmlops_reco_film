import pandas as pd
import os
from supabase import create_client, Client
from tqdm import tqdm
import numpy as np


def connect_to_supabase():
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")

    if not all([supabase_url, supabase_key]):
        raise ValueError(
            "Les variables d'environnement SUPABASE_URL et SUPABASE_KEY doivent être définies."
        )

    supabase_url = (
        f"https://{supabase_url}"
        if not supabase_url.startswith(("http://", "https://"))
        else supabase_url
    )

    return create_client(supabase_url, supabase_key)


def initialize_supabase_connection():
    try:
        return connect_to_supabase()
    except ValueError as ve:
        print(f"Erreur lors de la connexion à Supabase : {ve}")
    except Exception as e:
        print(
            f"Une erreur inattendue s'est produite lors de la connexion à Supabase : {e}"
        )
    exit(1)


def load_data(csv_path, table_name, supabase: Client, expected_types: dict, dtype=None):
    if dtype is None:
        dtype = expected_types

    # Modifier les types pour permettre les valeurs NA dans les colonnes d'entiers
    for col, typ in dtype.items():
        if typ == "int64":
            dtype[col] = "Int64"  # Utiliser le type nullable Int64 de pandas

    total_rows = len(pd.read_csv(csv_path))
    chunksize = 20000
    total_chunks = (total_rows // chunksize) + (1 if total_rows % chunksize != 0 else 0)

    for chunk in tqdm(
        pd.read_csv(csv_path, dtype=dtype, chunksize=chunksize),
        desc=f"Insertion des {total_rows} lignes de {table_name}",
        total=total_chunks,
        dynamic_ncols=True,
    ):
        chunk = chunk.where(pd.notnull(chunk), None)
        data = chunk.to_dict(orient="records")
        data = [
            {
                k: (
                    float(v)
                    if isinstance(v, (float, np.float64)) and not pd.isna(v)
                    else (v if not pd.isna(v) else None)
                )
                for k, v in record.items()
            }
            for record in data
        ]
        supabase.table(table_name).upsert(data).execute()


supabase = initialize_supabase_connection()

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
data_dir = os.path.join(project_root, "data")
raw_dir = os.path.join(data_dir, "raw")
processed_dir = os.path.join(data_dir, "processed")

# TODO: Ajouter les tables ratings, tags, links, genome_scores, genome_tags, movie_matrix, user_matrix
data_config = {
    "tables": {
        "movies": os.path.join(processed_dir, "movies.csv"),
        # "ratings": os.path.join(raw_dir, "ratings.csv"),
        # "tags": os.path.join(raw_dir, "tags.csv"),
        "links": os.path.join(raw_dir, "links.csv"),
        # "genome_scores": os.path.join(raw_dir, "genome-scores.csv"),
        # "genome_tags": os.path.join(raw_dir, "genome-tags.csv"),
        "movie_matrix": os.path.join(processed_dir, "movie_matrix.csv"),
        "user_matrix": os.path.join(processed_dir, "user_matrix.csv"),
    },
    "expected_types": {
        "movies": {
            "movieId": "int64",
            "title": "object",
            "genres": "object",
            "year": "int64",
            # Supprimer ou commenter la ligne suivante
            # "posterUrl": "object",
        },
        "ratings": {
            "userId": "int64",
            "movieId": "int64",
            "rating": "float64",
            "timestamp": "int64",
        },
        "tags": {
            "userId": "int64",
            "movieId": "int64",
            "tag": "object",
            "timestamp": "int64",
        },
        "links": {"movieId": "int64", "imdbId": "object", "tmdbId": "object"},
        "genome_scores": {"movieId": "int64", "tagId": "int64", "relevance": "float64"},
        "genome_tags": {"tagId": "int64", "tag": "object"},
        "movie_matrix": {
            "movieId": "int64",
            "(no genres listed)": "float64",
            "Action": "float64",
            "Adventure": "float64",
            "Animation": "float64",
            "Children": "float64",
            "Comedy": "float64",
            "Crime": "float64",
            "Documentary": "float64",
            "Drama": "float64",
            "Fantasy": "float64",
            "Film-Noir": "float64",
            "Horror": "float64",
            "IMAX": "float64",
            "Musical": "float64",
            "Mystery": "float64",
            "Romance": "float64",
            "Sci-Fi": "float64",
            "Thriller": "float64",
            "War": "float64",
            "Western": "float64",
        },
        "user_matrix": {
            "userId": "int64",
            "(no genres listed)": "float64",
            "Action": "float64",
            "Adventure": "float64",
            "Animation": "float64",
            "Children": "float64",
            "Comedy": "float64",
            "Crime": "float64",
            "Documentary": "float64",
            "Drama": "float64",
            "Fantasy": "float64",
            "Film-Noir": "float64",
            "Horror": "float64",
            "IMAX": "float64",
            "Musical": "float64",
            "Mystery": "float64",
            "Romance": "float64",
            "Sci-Fi": "float64",
            "Thriller": "float64",
            "War": "float64",
            "Western": "float64",
        },
    },
}

for table_name, file_path in data_config["tables"].items():
    if table_name in data_config["expected_types"]:
        load_data(
            file_path, table_name, supabase, data_config["expected_types"][table_name]
        )
    else:
        print(f"Attention : Aucun type attendu défini pour la table {table_name}")
        load_data(file_path, table_name, supabase, {})

print("Données chargées avec succès dans la base de données Supabase.")
