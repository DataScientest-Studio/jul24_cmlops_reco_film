from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

# Vérification des variables d'environnement
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception(
        "Les variables d'environnement SUPABASE_URL et SUPABASE_KEY doivent être définies"
    )

# Initialiser le client Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def sign_up(email: str, password: str):
    """Inscription d'un nouvel utilisateur"""
    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        return response
    except Exception as e:
        raise Exception(f"Erreur lors de l'inscription : {str(e)}")


def sign_in(email: str, password: str):
    """Connexion d'un utilisateur"""
    try:
        response = supabase.auth.sign_in_with_password(
            {"email": email, "password": password}
        )
        return response
    except Exception as e:
        raise Exception(f"Erreur lors de la connexion : {str(e)}")


def sign_out(session):
    """Déconnexion d'un utilisateur"""
    try:
        supabase.auth.sign_out()
        return True
    except Exception as e:
        raise Exception(f"Erreur lors de la déconnexion : {str(e)}")
