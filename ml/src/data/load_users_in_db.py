import pandas as pd
import os
from supabase import create_client, Client
from tqdm import tqdm
import numpy as np
from dotenv import load_dotenv
import bcrypt

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

# Fonction pour charger et insérer des utilisateurs depuis un fichier CSV
def load_users_from_csv(csv_file: str):
    # Charger le fichier CSV
    df = pd.read_csv(csv_file)

    for index, row in df.iterrows():
        user_id = row['userId']
        email = row['email']
        password = row['password']

        # Hacher le mot de passe
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Insérer l'utilisateur dans la table 'users'
        response = supabase.table('users').insert({
            'userId': user_id,
            'email': email,
            'password': hashed_password  # Assurez-vous que ce champ correspond à votre schéma
        }).execute()

        if response.error:
            print(f"Erreur lors de l'insertion de l'utilisateur {email}: {response.error}")

    print("Utilisateurs chargées avec succès dans la base de données Supabase.")


# Initialiser la connexion à Supabase
supabase = initialize_supabase_connection()

# Définir le chemin vers le dossier contenant les données brutes
base_dir = os.path.dirname(os.path.abspath(__file__))
# Construire le chemin vers le répertoire contenant les données traitées
data_dir = os.path.join(base_dir, '..', '..', 'data', 'processed')

csv_file_path = os.path.join(data_dir, 'users.csv')

# Remplacez par le chemin vers votre fichier CSV
load_users_from_csv(csv_file_path)



