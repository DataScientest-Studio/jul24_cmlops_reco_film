CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE movies (
    "movieId" INTEGER PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    genres VARCHAR(255),
    year INTEGER,
    "posterUrl" VARCHAR(255)
);

CREATE TABLE ratings (
    "userId" INTEGER,
    "movieId" INTEGER,
    rating FLOAT,
    timestamp INTEGER,
    PRIMARY KEY ("userId", "movieId"),
    FOREIGN KEY ("movieId") REFERENCES movies("movieId")
);

CREATE TABLE tags (
    "userId" INTEGER,
    "movieId" INTEGER,
    tag VARCHAR(255),
    timestamp INTEGER,
    FOREIGN KEY ("movieId") REFERENCES movies("movieId")
);

CREATE TABLE links (
    "movieId" INTEGER PRIMARY KEY,
    "imdbId" VARCHAR(10),
    "tmdbId" VARCHAR(10),
    FOREIGN KEY ("movieId") REFERENCES movies("movieId")
);

CREATE TABLE genome_scores (
    "movieId" INTEGER,
    "tagId" INTEGER,
    relevance FLOAT,
    FOREIGN KEY ("movieId") REFERENCES movies("movieId")
);

CREATE TABLE genome_tags (
    "tagId" INTEGER PRIMARY KEY,
    tag VARCHAR(255)
);

CREATE TABLE movie_matrix (
    "movieId" INTEGER PRIMARY KEY,
    "(no genres listed)" FLOAT,
    "Action" FLOAT,
    "Adventure" FLOAT,
    "Animation" FLOAT,
    "Children" FLOAT,
    "Comedy" FLOAT,
    "Crime" FLOAT,
    "Documentary" FLOAT,
    "Drama" FLOAT,
    "Fantasy" FLOAT,
    "Film-Noir" FLOAT,
    "Horror" FLOAT,
    "IMAX" FLOAT,
    "Musical" FLOAT,
    "Mystery" FLOAT,
    "Romance" FLOAT,
    "Sci-Fi" FLOAT,
    "Thriller" FLOAT,
    "War" FLOAT,
    "Western" FLOAT,
    FOREIGN KEY ("movieId") REFERENCES movies("movieId")
);

CREATE TABLE user_matrix (
    "userId" INTEGER PRIMARY KEY,
    "(no genres listed)" FLOAT,
    "Action" FLOAT,
    "Adventure" FLOAT,
    "Animation" FLOAT,
    "Children" FLOAT,
    "Comedy" FLOAT,
    "Crime" FLOAT,
    "Documentary" FLOAT,
    "Drama" FLOAT,
    "Fantasy" FLOAT,
    "Film-Noir" FLOAT,
    "Horror" FLOAT,
    "IMAX" FLOAT,
    "Musical" FLOAT,
    "Mystery" FLOAT,
    "Romance" FLOAT,
    "Sci-Fi" FLOAT,
    "Thriller" FLOAT,
    "War" FLOAT,
    "Western" FLOAT
);
