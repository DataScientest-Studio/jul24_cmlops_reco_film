import pandas as pd
from sklearn.preprocessing import LabelEncoder
import os


def read_ratings(ratings_csv, data_dir="ml/data/raw") -> pd.DataFrame:
    data = pd.read_csv(os.path.join(data_dir, ratings_csv))
    temp = pd.DataFrame(LabelEncoder().fit_transform(data["movieId"]))
    data["movieId"] = temp
    return data


def read_movies(movies_csv, data_dir="ml/data/raw") -> pd.DataFrame:
    df = pd.read_csv(os.path.join(data_dir, movies_csv))
    genres = df["genres"].str.get_dummies(sep="|")
    result_df = pd.concat([df[["movieId", "title"]], genres], axis=1)
    return result_df


def process_movies(
    movies_csv,
    input_dir="ml/data/raw",
    output_dir="ml/data/processed",
):
    df = pd.read_csv(os.path.join(input_dir, movies_csv))
    df["year"] = df["title"].str.extract(r"\((\d{4})\)$")
    df["title"] = df["title"].str.replace(r"\s*\(\d{4}\)$", "", regex=True)
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    genres = df["genres"].str.get_dummies(sep="|")
    df = pd.concat([df[["movieId", "title", "year"]], genres], axis=1)
    df.to_csv(os.path.join(output_dir, movies_csv), index=False)
    return df


def create_user_matrix(ratings, movies, output_dir="ml/data/processed"):
    movie_ratings = ratings.merge(movies, on="movieId", how="inner")
    movie_ratings = movie_ratings.drop(
        ["movieId", "timestamp", "title", "rating", "year"], axis=1
    )
    user_matrix = movie_ratings.groupby("userId").agg(
        "mean",
    )
    user_matrix.to_csv(os.path.join(output_dir, "user_matrix.csv"))
    return user_matrix


if __name__ == "__main__":
    user_ratings = read_ratings("ratings.csv")
    movies = read_movies("movies.csv")
    process_movies("movies.csv")
    user_matrix = create_user_matrix(user_ratings, movies)
    movies = movies.drop(["title", "year"], axis=1)
    movies.to_csv("ml/data/processed/movie_matrix.csv", index=False)
