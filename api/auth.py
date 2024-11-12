from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette import status
from fastapi.security import  OAuth2PasswordBearer
from jose import jwt, JWTError
import os
from dotenv import load_dotenv
from prometheus_client import Counter, Histogram, CollectorRegistry
import time
import re

# Création d'un routeur pour gérer les routes d'authentification
router = APIRouter(
    prefix='/auth',  # Préfixe pour toutes les routes dans ce routeur
    tags=['auth']  # Tag pour la documentation
)

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

# Clé secrète pour le JWT (à remplacer par une variable d'environnement en production)
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')  # Algorithme utilisé pour encoder le JWT

# Vérification des variables d'environnement SUPABASE_URL et SUPABASE_KEY
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Les variables d'environnement SUPABASE_URL et SUPABASE_KEY doivent être définies")

# Initialiser le client Supabase
from supabase import create_client, Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Modèle Pydantic pour la création d'un utilisateur
class CreateUserRequest(BaseModel):
    email: str  # Email d'utilisateur
    password: str  # Mot de passe

def sign_up(create_user_request: CreateUserRequest):
    """Inscription d'un nouvel utilisateur"""
    try:
        response = supabase.auth.sign_up({
            "email": create_user_request.email,
            "password": create_user_request.password
        })
        return response
    except Exception as e:
        raise Exception(f"Erreur lors de l'inscription : {str(e)}")

def sign_in(create_user_request: CreateUserRequest):
    """Connexion d'un utilisateur"""
    try:
        response = supabase.auth.sign_in_with_password({
            "email": create_user_request.email,
            "password": create_user_request.password
        })
        return response
    except Exception as e:
        raise Exception(f"Erreur lors de la connexion : {str(e)}")

def sign_out():
    """Déconnexion d'un utilisateur"""
    try:
        supabase.auth.sign_out()
        return True
    except Exception as e:
        raise Exception(f"Erreur lors de la déconnexion : {str(e)}")

# Compteurs et histogrammes pour les métriques Prometheus
collector = CollectorRegistry()
user_creation_counter = Counter(
    name='user_creation_requests_total',
    documentation='Total number of user creation requests',
    labelnames=['status_code'],
)
login_requests_counter = Counter(
    name='login_requests_total',
    documentation='Total number of login requests',
    labelnames=['status_code'],
)
user_creation_duration_histogram = Histogram(
    name='user_creation_duration_seconds',
    documentation='Duration of user creation requests in seconds',
    labelnames=['status_code'],
)
login_duration_histogram = Histogram(
    name='login_duration_seconds',
    documentation='Duration of login requests in seconds',
    labelnames=['status_code'],
)
error_counter = Counter(
    name='user_creation_errors_total',
    documentation='Total number of user creation errors',
    labelnames=['error_type'],
)

# Fonction pour valider l'email avec une expression régulière
def validate_email(email: str) -> str:
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if re.match(email_regex, email) is None:
        return "L'adresse e-mail n'est pas valide."
    return None

# Fonction pour valider le mot de passe selon des critères de sécurité
def validate_password(password: str) -> str:
    if len(password) < 12:
        return "Le mot de passe doit contenir au moins 12 caractères."
    if not re.search(r"\d", password):
        return "Le mot de passe doit contenir au moins un chiffre."
    if not re.search(r"[A-Z]", password):
        return "Le mot de passe doit contenir au moins une lettre majuscule."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Le mot de passe doit contenir au moins un caractère spécial."
    return None

# Fonction pour vérifier si l'utilisateur existe déjà par email
def user_exists_by_email(email: str) -> bool:
    users = supabase.auth.admin.list_users()
    for user in users.data:
        if user.email == email:
            return True  # L'utilisateur existe déjà
    return False  # L'utilisateur n'existe pas

# Route pour créer un nouvel utilisateur avec validation et métriques Prometheus
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(create_user_request: CreateUserRequest):
    start_time = time.time()  # Démarrer le chronomètre

    # Valider l'email de l'utilisateur
    email_error = validate_email(create_user_request.email)
    if email_error:
        error_counter.labels(error_type='invalid_email').inc()
        raise HTTPException(status_code=400, detail=email_error)

    # Valider le mot de passe de l'utilisateur
    password_error = validate_password(create_user_request.password)
    if password_error:
        error_counter.labels(error_type='invalid_password').inc()
        raise HTTPException(status_code=400, detail=password_error)

    # Vérifiez si l'utilisateur existe déjà par email
    existing_user = user_exists_by_email(create_user_request.email)
    if existing_user:
        error_counter.labels(error_type='username_already_registered').inc()
        user_creation_counter.labels(status_code='400').inc()
        raise HTTPException(status_code=400, detail="L'utilisateur est déjà enregistré.")

    # Inscrire l'utilisateur dans Supabase si toutes les validations passent
    sign_up(create_user_request)

    duration = time.time() - start_time  # Calculer la durée de la création de l'utilisateur
    user_creation_duration_histogram.labels(status_code='201').observe(duration)

    user_creation_counter.labels(status_code='201').inc()  # Incrémenter le compteur de succès

# Fonction pour authentifier un utilisateur
def authenticate_user(username: str, password: str):
   """Authentifie un utilisateur avec son nom d'utilisateur et son mot de passe."""
   user = supabase.auth.admin.get_user_by_email(username)  # Récupérer l'utilisateur par email
   if not user:
       login_requests_counter.labels(status_code='404').inc()
       raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")

   if not supabase.auth.verify_password(password, user.password):  # Vérifier le mot de passe (ajuster selon votre implémentation)
       login_requests_counter.labels(status_code='401').inc()
       raise HTTPException(status_code=401, detail="Mot de passe incorrect.")

   return user  # Retourner l'utilisateur si l'authentification réussit

# Fonction pour créer un token d'accès
def create_access_token(username: str, user_id: int, expires_delta: timedelta):
   """Crée un token JWT pour authentifier l'utilisateur."""
   encode = {'sub': username, 'id': user_id}  # Charge utile du token
   expires = datetime.utcnow() + expires_delta  # Définit la date d'expiration
   encode.update({'exp': expires})  # Ajoute la date d'expiration à la charge utile
   return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)  # Encode le token

# Fonction pour obtenir l'utilisateur actuel à partir du token
async def get_current_user(token: Annotated[str, Depends(OAuth2PasswordBearer)]):
   """Récupère les informations sur l'utilisateur actuel à partir du token JWT."""
   try:
       payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # Décode le token
       username: str = payload.get('sub')  # Récupère le nom d'utilisateur
       user_id: int = payload.get('id')  # Récupère l'ID de l'utilisateur
       if username is None or user_id is None:
           raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')  # Erreur si les données sont manquantes
       return {'username': username, 'id': user_id}  # Retourne les données de l'utilisateur
   except JWTError:
       raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')  # Erreur si le token est invalide