from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

username=os.getenv("POSTGRES_USER")
password=os.getenv("POSTGRES_PASSWORD")
database=os.getenv("POSTGRES_DB")
host=os.getenv("POSTGRES_HOST")
port=os.getenv("POSTGRES_PORT")

# URL de la base de données PostgreSQL
SQLALCHEMY_DATABASE_URL = f'postgresql://{username}:{password}@{host}:{port}/{database}'

# Création de l'engine de la base de données
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Création d'une session locale pour interagir avec la base de données
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Création de la classe de base pour les modèles SQLAlchemy
Base = declarative_base()
