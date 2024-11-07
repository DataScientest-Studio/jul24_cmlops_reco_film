from fastapi import FastAPI, HTTPException, Depends
from typing import List, Dict
from supabase import create_client, Client
from functools import lru_cache
import os

app = FastAPI()


def connect_to_supabase():
    supabase_url = os.environ.get(
        "SUPABASE_URL", "http://kong:8000"
    )  # Modification ici
    supabase_key = os.environ.get("SUPABASE_KEY")

    print(f"Tentative de connexion avec URL: {supabase_url}")  # Debug

    if not all([supabase_url, supabase_key]):
        raise ValueError(
            "Les variables d'environnement SUPABASE_URL et SUPABASE_KEY doivent être définies."
        )

    return create_client(supabase_url, supabase_key)


def initialize_supabase_connection():
    try:
        supabase = connect_to_supabase()
        # Test de connexion
        test = supabase.table("movies").select("*").limit(1).execute()
        print("Connexion à Supabase réussie!")
        return supabase
    except ValueError as ve:
        print(f"Erreur de configuration : {ve}")
        raise ve
    except Exception as e:
        print(f"Erreur de connexion : {str(e)}")
        print(f"Type d'erreur : {type(e)}")
        raise e


supabase = initialize_supabase_connection()


@app.get("/movie/{movie_id}", response_model=Dict)
async def get_movie_info(
    movie_id: int,
):
    result = (
        supabase.table("movies")
        .select("*")
        .eq("movieId", movie_id)
        .limit(1)
        .single()
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Film non trouvé")

    return result.data


@app.get("/user/{user_id}")
async def get_user_info(
    user_id: int,
):
    return (
        supabase.table("user_matrix")
        .select("*")
        .eq("userId", user_id)
        .limit(1)
        .single()
        .execute()
        .data
    )


@app.get("/movie/{movie_id}/ratings")
async def get_movie_ratings(
    movie_id: int,
    limit: int = 1000,
):
    return (
        supabase.table("ratings")
        .select("*")
        .eq("movieId", movie_id)
        .limit(limit)
        .execute()
        .data
    )


@app.post("/get_tmdb_ids")
async def get_tmdb_ids(
    movie_ids: List[int],
):
    if not movie_ids:
        return {}

    result = (
        supabase.table("links")
        .select("movieId, tmdbId")
        .in_("movieId", movie_ids)
        .execute()
    )

    return {row["movieId"]: row["tmdbId"] for row in result.data}
