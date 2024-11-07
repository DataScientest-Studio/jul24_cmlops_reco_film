import os
import pandas as pd

def read_ratings(ratings_csv: str) -> pd.DataFrame:
    """Lit le fichier CSV contenant les évaluations des films et retourne un DataFrame Pandas.

    Args:
        ratings_csv (str): Le nom du fichier CSV contenant les évaluations.

    Returns:
        pd.DataFrame: Un DataFrame contenant les données des évaluations.

    Raises:
        FileNotFoundError: Si le fichier CSV n'est pas trouvé.
        pd.errors.EmptyDataError: Si le fichier CSV est vide.
        pd.errors.ParserError: Si le fichier CSV ne peut pas être analysé.
    """

    # Obtenir le répertoire du script actuel
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Construire le chemin vers le répertoire contenant les données traitées
    data_dir = os.path.join(base_dir, '..', 'data', 'processed')

    # Construire le chemin complet vers le fichier CSV
    csv_file_path = os.path.join(data_dir, ratings_csv)

    try:
        # Lire le fichier CSV et retourner un DataFrame Pandas
        data = pd.read_csv(csv_file_path)
        print("Dataset ratings loaded")  # Confirmation du chargement réussi
        return data

    except FileNotFoundError:
        print(f"Erreur : Le fichier '{csv_file_path}' n'a pas été trouvé.")
        raise  # Relancer l'exception pour signaler l'erreur

    except pd.errors.EmptyDataError:
        print(f"Erreur : Le fichier '{csv_file_path}' est vide.")
        raise  # Relancer l'exception pour signaler l'erreur

    except pd.errors.ParserError:
        print(f"Erreur : Impossible d'analyser le fichier '{csv_file_path}'.")
        raise  # Relancer l'exception pour signaler l'erreur

    except Exception as e:
        print(f"Erreur lors du chargement des données : {e}")
        raise  # Relancer l'exception pour signaler l'erreur