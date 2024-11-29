import pandas as pd
import os
from passlib.context import CryptContext

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def load_data(data_directory):
    df_ratings = pd.read_csv(f'{data_directory}/to_ingest/bronze/ratings.csv')
    df_movies = pd.read_csv(f'{data_directory}/to_ingest/bronze/movies.csv')
    df_links = pd.read_csv(f'{data_directory}/to_ingest/bronze/links.csv')
    print(f'ratings, movies and links loaded from {data_directory}/to_ingest/bronze directory')
    return df_ratings, df_movies, df_links

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

def preprocessing_ratings(df_ratings) -> pd.DataFrame:
    """
    Lecture du fichier CSV des évaluations et application de la moyenne bayésienne.

    Args:
        ratings_file (str): Chemin vers le fichier CSV contenant les évaluations.

    Returns:
        pd.DataFrame: DataFrame contenant les évaluations traitées.
    """

    # Statistiques par film : quantité et moyenne des notes
    movies_stats = df_ratings.groupby('movieId').agg({'rating': ['count', 'mean']})
    movies_stats.columns = ['count', 'mean']

    # Calculer les moyennes nécessaires pour la moyenne bayésienne
    C = movies_stats['count'].mean()  # Moyenne de la quantité de notes
    M = movies_stats['mean'].mean()    # Moyenne brute des notes

    # Calculer la moyenne bayésienne par film
    movies_stats['bayesian_mean'] = movies_stats.apply(
        lambda x: bayesienne_mean(df_ratings[df_ratings['movieId'] == x.name]['rating'], M, C), axis=1)

    # Ajouter la colonne bayesian_mean au DataFrame original
    df_ratings = df_ratings.merge(movies_stats[['bayesian_mean']], on='movieId', how='left')

    print("Application de la moyenne bayésienne sur la colonne rating effectuée")

    return df_ratings

def preprocessing_movies(df_movies) -> pd.DataFrame:
    """
    Lecture du fichier CSV des films et traitement des données.

    Args:
        movies_file (str): Chemin vers le fichier CSV contenant les films.

    Returns:
        pd.DataFrame: DataFrame contenant les films traités.
    """

    # Traitement des genres et extraction de l'année
    print("Création d'une colonne year et passage des genres en liste de genres")

    # Séparer les genres sur les pipes
    # Séparer les genres sur les pipes et les joindre par des virgules
    df_movies['genres'] = df_movies['genres'].apply(lambda x: ', '.join(x.split("|")))

    # Extraction de l'année et mise à jour du titre
    df_movies['year'] = df_movies['title'].str.extract(r'\((\d{4})\)')[0]

    # Nettoyer le titre en retirant l'année
    df_movies['title'] = df_movies['title'].str.replace(r' \(\d{4}\)', '', regex=True)

    # Remplir les valeurs manquantes avec la méthode forward fill
    df_movies.ffill(inplace=True)

    return df_movies

def preprocessing_links(df_links) -> pd.DataFrame:
   """
   Chargement du dataset des liens et modification du type de tmdbId.

   Args:
       links_file (str): Chemin vers le fichier CSV contenant les liens.

   Returns:
       pd.DataFrame: DataFrame contenant les liens traités.
   """

   print('Modification du type de la colonne tmdbId en int')
   # Remplacer les valeurs manquantes par 0 et convertir en entier
   df_links['tmdbId'] = df_links.tmdbId.fillna(0).astype(int)

   return df_links

def create_users():
    print("Création des utilisateurs _ fichier users.csv")
    username = []
    email = []
    password = []

    for i in range(1, 501):
        username.append('user'+str(i))
        email.append('user'+str(i)+'@example.com')
        password.append('password'+str(i))

    hached_password = [bcrypt_context.hash(i) for i in password]

    # Créer un DataFrame
    df_users = pd.DataFrame({'username': username, 'email': email, 'hached_password': hached_password})

    return df_users

def save_data(df_ratings, df_movies, df_links, df_users, data_directory):
    df_ratings.to_csv(f'{data_directory}/to_ingest/silver/processed_ratings.csv', index=False)
    df_movies.to_csv(f'{data_directory}/to_ingest/silver/processed_movies.csv', index=False)
    df_links.to_csv(f'{data_directory}/to_ingest/silver/processed_links.csv', index=False)
    df_users.to_csv(f'{data_directory}/to_ingest/silver/users.csv', index=False)
    print(f'processed_ratings, processed_movies, processed_links and users loaded in {data_directory}/to_ingest/silver directory')

if __name__ == "__main__":
    data_directory = 'data'
    df_ratings, df_movies, df_links = load_data(data_directory)
    preprocessing_ratings(df_ratings)
    preprocessing_movies(df_movies)
    preprocessing_links(df_links)
    df_users = create_users()
    save_data(df_ratings, df_movies, df_links, df_users, data_directory)