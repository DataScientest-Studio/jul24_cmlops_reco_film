from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette import status
from database import get_db_connection
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
import os
from dotenv import load_dotenv
from prometheus_client import Counter, Histogram, CollectorRegistry
import time
import re
import psycopg2

# Création d'un routeur pour gérer les routes d'authentification
router = APIRouter(
    prefix='/auth',  # Préfixe pour toutes les routes dans ce routeur
    tags=['auth']    # Tag pour la documentation
)
# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

# Clé secrète pour le JWT (à remplacer par une variable d'environnement en production)
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')  # Algorithme utilisé pour encoder le JWT

# Contexte de hachage pour le mot de passe
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# Définition du schéma de sécurité pour le token
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

# Modèle Pydantic pour la création d'un utilisateur
class CreateUserRequest(BaseModel):
    username: str  # Nom d'utilisateur
    email: str  # Adresse e-mail
    password: str  # Mot de passe

# Modèle Pydantic pour le token d'accès
class Token(BaseModel):
    access_token: str  # Le token d'accès
    token_type: str    # Type de token (généralement "bearer")


# Compteurs et histogrammes
collector = CollectorRegistry()

# Compteurs et histogrammes pour les métriques
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

# Fonction pour valider le nom d'utilisateur
def validate_username(username):
    if re.match("^[A-Za-z0-9_]+$", username) is None:
        return "Le nom d'utilisateur ne doit contenir que des lettres, chiffres et underscores."
    return None

def validate_email(email):
    # Expression régulière pour valider une adresse e-mail
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

    if re.match(email_regex, email) is None:
        return "L'adresse e-mail n'est pas valide."
    return None

# Fonction pour valider le mot de passe
def validate_password(password):
    if len(password) < 12:
        return "Le mot de passe doit contenir au moins 12 caractères."
    if not re.search(r"\d", password):
        return "Le mot de passe doit contenir au moins un chiffre."
    if not re.search(r"[A-Z]", password):
        return "Le mot de passe doit contenir au moins une lettre majuscule."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Le mot de passe doit contenir au moins un caractère spécial."
    return None

# Route pour créer un nouvel utilisateur
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(create_user_request: CreateUserRequest):
    start_time = time.time()

    # Validation checks
    username_error = validate_username(create_user_request.username)
    if username_error:
        error_counter.labels(error_type='invalid_username').inc()
        raise HTTPException(status_code=400, detail=username_error)

    mail_error = validate_email(create_user_request.email)
    if mail_error:
        error_counter.labels(error_type='invalid_mail').inc()
        raise HTTPException(status_code=400, detail=mail_error)

    password_error = validate_password(create_user_request.password)
    if password_error:
        error_counter.labels(error_type='invalid_password').inc()
        raise HTTPException(status_code=400, detail=password_error)

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Vérifier si l'email existe déjà
                cur.execute("SELECT email FROM users WHERE email = %s", (create_user_request.email,))
                if cur.fetchone() is not None:
                    error_counter.labels(error_type='username_already_registered').inc()
                    user_creation_counter.labels(status_code='400').inc()
                    raise HTTPException(status_code=400, detail="Email already registered")

                # Créer le nouvel utilisateur
                hached_password = bcrypt_context.hash(create_user_request.password)
                cur.execute(
                    """
                    INSERT INTO users (username, email, hached_password)
                    VALUES (%s, %s, %s)
                    RETURNING userid, username, email
                    """,
                    (create_user_request.username, create_user_request.email, hached_password)
                )
                conn.commit()
                new_user = cur.fetchone()

    except psycopg2.Error as e:
        error_counter.labels(error_type='database_error').inc()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    duration = time.time() - start_time
    user_creation_duration_histogram.labels(status_code='201').observe(duration)
    user_creation_counter.labels(status_code='201').inc()

    return {
        "userId": new_user[0],
        "username": new_user[1],
        "email": new_user[2]
    }

# Route pour obtenir un token d'accès
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    start_time = time.time()
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        login_requests_counter.labels(status_code='401').inc()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')

    token = create_access_token(user['email'], user['userId'], timedelta(minutes=30))
    duration = time.time() - start_time
    login_duration_histogram.labels(status_code='200').observe(duration)
    login_requests_counter.labels(status_code='200').inc()

    return {"access_token": token, "token_type": "bearer", "username": user['username'], "userId": user['userId']}

async def authenticate_user(email: str, password: str):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT userid, username, email, hached_password FROM users WHERE email = %s",
                    (email,)
                )
                user = cur.fetchone()

                if not user:
                    login_requests_counter.labels(status_code='404').inc()
                    raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

                if not bcrypt_context.verify(password, user[3]):
                    login_requests_counter.labels(status_code='401').inc()
                    raise HTTPException(status_code=401, detail="Mot de passe incorrect")

                return {
                    'userId': user[0],
                    'username': user[1],
                    'email': user[2]
                }
    except psycopg2.Error as e:
        error_counter.labels(error_type='database_error').inc()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Fonction pour créer un token d'accès
def create_access_token(email: str, user_id: int, expires_delta: timedelta):
    encode = {'sub': email, 'id': user_id}  # Charge utile du token
    expires = datetime.utcnow() + expires_delta  # Définit la date d'expiration
    encode.update({'exp': expires})  # Ajoute la date d'expiration à la charge utile
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)  # Encode le token

# Fonction pour obtenir l'utilisateur actuel à partir du token
async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # Décode le token
        email: str = payload.get('sub')  # Récupère le nom d'utilisateur
        user_id: int = payload.get('id')  # Récupère l'ID de l'utilisateur
        if email is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')  # Erreur si les donnees sont manquantes
        return {'email': email, 'id': user_id}  # Retourne les données de l'utilisateur
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')  # Erreur si le token est invalide