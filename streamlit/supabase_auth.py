from supabase import create_client, Client
import os

# Vérification des variables d'environnement
SUPABASE_URL = os.environ.get("SUPABASE_URL", "http://kong:8000")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

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
