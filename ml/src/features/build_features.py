import pandas as pd
from sklearn.preprocessing import LabelEncoder
import os


def read_ratings(ratings_csv, data_dir="ml/data/raw") -> pd.DataFrame:
    data = pd.read_csv(os.path.join(data_dir, ratings_csv))
    # TODO: vérifier si ça marche sans ça. MAJ : ça a l'air de marcher sans, le model fait de meilleurs predictions
    # temp = pd.DataFrame(LabelEncoder().fit_transform(data["movieId"]))
    # data["movieId"] = temp
    return data


def read_movies(movies_csv, data_dir="ml/data/raw") -> pd.DataFrame:
    df = pd.read_csv(os.path.join(data_dir, movies_csv))
    genres = df["genres"].str.get_dummies(sep="|")
    result_df = pd.concat([df[["movieId", "title"]], genres], axis=1)
    return result_df


def process_movies(
    movies_csv,
    ratings_csv,
    input_dir="ml/data/raw",
    output_dir="ml/data/processed",
):
    movies = pd.read_csv(os.path.join(input_dir, movies_csv))
    ratings = pd.read_csv(os.path.join(input_dir, ratings_csv))
    links2 = pd.read_csv(os.path.join(input_dir, "links2.csv"))

    movies["year"] = movies["title"].str.extract(r"\((\d{4})\)$")
    movies["title"] = movies["title"].str.replace(r"\s*\(\d{4}\)$", "", regex=True)
    movies["year"] = pd.to_numeric(movies["year"], errors="coerce").astype("Int64")
    movie_stats = ratings.groupby("movieId").agg(
        rating=("rating", "mean"),
        numRatings=("rating", "count"),
        lastRatingTimestamp=("timestamp", "max"),
    )
    movies = movies.merge(movie_stats, on="movieId", how="left")
    movies["numRatings"] = movies["numRatings"].astype("Int64")
    movies["lastRatingTimestamp"] = movies["lastRatingTimestamp"].astype("Int64")

    links2 = links2.set_index("movieId")
    links2 = links2.drop(["imdbId", "tmdbId", "Unnamed: 0"], axis=1)
    links2 = links2.rename(columns={"cover_link": "posterUrl"})
    movies = movies.merge(links2, on="movieId", how="left")

    movies.to_csv(os.path.join(output_dir, "movies.csv"), index=False)
    return movies


def create_user_matrix(ratings, movies, output_dir="ml/data/processed"):
    movie_ratings = ratings.merge(movies, on="movieId", how="inner")
    movie_ratings = movie_ratings.drop(
        ["movieId", "timestamp", "title", "rating"], axis=1
    )
    user_matrix = movie_ratings.groupby("userId").agg(
        "mean",
    )
    user_matrix.to_csv(os.path.join(output_dir, "user_matrix.csv"))
    return user_matrix


if __name__ == "__main__":
    user_ratings = read_ratings("ratings.csv")
    movies = read_movies("movies.csv")
    process_movies("movies.csv", "ratings.csv")
    user_matrix = create_user_matrix(user_ratings, movies)
    movies = movies.drop(["title"], axis=1)
    movies.to_csv("ml/data/processed/movie_matrix.csv", index=False)
