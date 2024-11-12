
from fastapi import FastAPI, status, Depends
from auth import get_current_user, router as auth_router # Importation des fonctions d'authentification et du routeur
from predict import router as predict_router # Importation des fonctions de predictions
from prometheus_fastapi_instrumentator import Instrumentator
from dotenv import load_dotenv
import os

# Création de l'application FastAPI
app = FastAPI()

# Créez un instrumentateur et configurez-le
instrumentator = Instrumentator()

# Instrumenter l'application et exposer les métriques
instrumentator.instrument(app).expose(app)

# Inclusion du routeur d'authentification
app.include_router(auth_router)
app.include_router(predict_router)

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

# Route pour obtenir les informations de l'utilisateur actuel
@app.get("/", status_code=status.HTTP_200_OK)
async def user(current_user: dict = Depends(get_current_user)):
    """Récupère les informations sur l'utilisateur actuel."""
    return current_user  # Retourne les informations de l'utilisateur actuel

