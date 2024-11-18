import pandas as pd
import os
from passlib.context import CryptContext
from tqdm import tqdm

# localisation du fichier
base_dir = os.path.dirname(os.path.abspath(__file__))

def bayesienne_mean(df, M, C):
    """
    Calcule la moyenne bayésienne des notes d'un film.

    Args:
        df (pd.Series): La série de notes du film.
        M (float): La moyenne brute des notes des films.
        C (float): La moyenne de la quantité de notes.

    Returns:
        float: La moyenne bayésienne calculée.
    """
    moy_ba = (C * M + df.sum()) / (C + df.count())
    return moy_ba

def preprocessing_ratings(ratings_file) -> pd.DataFrame:
    """
    Lecture du fichier CSV des évaluations et application de la moyenne bayésienne.

    Args:
        ratings_file (str): Chemin vers le fichier CSV contenant les évaluations.

    Returns:
        pd.DataFrame: DataFrame contenant les évaluations traitées.
    """
    # Lire le fichier CSV
    df = pd.read_csv(ratings_file)
    print("Dataset ratings chargé")

    # Statistiques par film : quantité et moyenne des notes
    movies_stats = df.groupby('movieId').agg({'rating': ['count', 'mean']})
    movies_stats.columns = ['count', 'mean']

    # Calculer les moyennes nécessaires pour la moyenne bayésienne
    C = movies_stats['count'].mean()  # Moyenne de la quantité de notes
    M = movies_stats['mean'].mean()    # Moyenne brute des notes

    # Calculer la moyenne bayésienne par film
    movies_stats['bayesian_mean'] = movies_stats.apply(
        lambda x: bayesienne_mean(df[df['movieId'] == x.name]['rating'], M, C), axis=1)

    # Ajouter la colonne bayesian_mean au DataFrame original
    df = df.merge(movies_stats[['bayesian_mean']], on='movieId', how='left')

    print("Application de la moyenne bayésienne sur la colonne rating effectuée")

    # Définir le chemin vers le dossier 'processed' pour enregistrer le fichier traité
    output_dir = os.path.join(base_dir, '..', '..', 'data',"processed")
    output_file = os.path.join(output_dir, "processed_ratings.csv")

    # Créer le dossier 'processed' s'il n'existe pas
    os.makedirs(output_dir, exist_ok=True)

    # Enregistrer le DataFrame en tant que fichier CSV
    try:
        df.to_csv(output_file, index=False)  # Enregistrer sans l'index
        print(f"Fichier enregistré avec succès sous {output_file}.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de l'enregistrement du fichier : {e}")

    return df

def preprocessing_movies(movies_file) -> pd.DataFrame:
    """
    Lecture du fichier CSV des films et traitement des données.

    Args:
        movies_file (str): Chemin vers le fichier CSV contenant les films.

    Returns:
        pd.DataFrame: DataFrame contenant les films traités.
    """
    # Lire le fichier CSV
    df = pd.read_csv(movies_file)
    print("Dataset movies chargé")

    # Traitement des genres et extraction de l'année
    print("Création d'une colonne year et passage des genres en liste de genres")

    # Séparer les genres sur les pipes
    # Séparer les genres sur les pipes et les joindre par des virgules
    df['genres'] = df['genres'].apply(lambda x: ', '.join(x.split("|")))

    # Extraction de l'année et mise à jour du titre
    df['year'] = df['title'].str.extract(r'\((\d{4})\)')[0]

    # Nettoyer le titre en retirant l'année
    df['title'] = df['title'].str.replace(r' \(\d{4}\)', '', regex=True)

    # Remplir les valeurs manquantes avec la méthode forward fill
    df.ffill(inplace=True)

    # Définir le chemin pour enregistrer le fichier traité
    output_dir = os.path.join(base_dir, '..', '..', 'data',"processed")
    output_file = os.path.join(output_dir, "processed_movies.csv")

    # Créer le dossier 'processed' s'il n'existe pas
    os.makedirs(output_dir, exist_ok=True)

    # Enregistrer le DataFrame en tant que fichier CSV
    try:
        df.to_csv(output_file, index=False)  # Enregistrer sans l'index
        print(f"Fichier enregistré avec succès sous {output_file}.")

    except Exception as e:
        print(f"Une erreur s'est produite lors de l'enregistrement du fichier : {e}")

    return df

def preprocessing_links(links_file) -> pd.DataFrame:
   """
   Chargement du dataset des liens et modification du type de tmdbId.

   Args:
       links_file (str): Chemin vers le fichier CSV contenant les liens.

   Returns:
       pd.DataFrame: DataFrame contenant les liens traités.
   """
   # Lire le fichier CSV
   df = pd.read_csv(links_file)
   print("Dataset links chargé")

   print('Modification du type de la colonne tmdbId en int')
   # Remplacer les valeurs manquantes par 0 et convertir en entier
   df['tmdbId'] = df.tmdbId.fillna(0).astype(int)

   # Définir le chemin pour enregistrer le fichier traité
   output_dir = os.path.join(base_dir, '..', '..', 'data',"processed")
   output_file = os.path.join(output_dir, "processed_links.csv")

   # Créer le dossier 'processed' s'il n'existe pas
   os.makedirs(output_dir, exist_ok=True)

   # Enregistrer le DataFrame en tant que fichier CSV
   try:
       df.to_csv(output_file, index=False)  # Enregistrer sans l'index
       print(f"Fichier enregistré avec succès sous {output_file}.")

   except Exception as e:
       print(f"Une erreur s'est produite lors de l'enregistrement du fichier : {e}")

   return df

if __name__ == "__main__":
    # Chargement des datasets
    # Obtenir le répertoire du script actuel
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, '..', '..', 'data', 'raw')
    ratings_file = os.path.join(data_dir, "ratings.csv")
    movies_file = os.path.join(data_dir, "movies.csv")
    links_file = os.path.join(data_dir, "links.csv")
    preprocessing_ratings(ratings_file)
    preprocessing_movies(movies_file)
    preprocessing_links(links_file)