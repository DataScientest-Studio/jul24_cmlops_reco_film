CREATE TABLE movies (
    "movieId" INTEGER PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    genres VARCHAR(255),
    year INTEGER,
    "posterUrl" VARCHAR(255),
    rating FLOAT DEFAULT 0,
    "numRatings" INTEGER DEFAULT 0,
    "lastRatingTimestamp" INTEGER
);

CREATE TABLE links (
    "movieId" INTEGER PRIMARY KEY,
    "imdbId" VARCHAR(10),
    "tmdbId" VARCHAR(10),
    FOREIGN KEY ("movieId") REFERENCES movies("movieId")
);

CREATE TABLE users (
    "userId" INTEGER PRIMARY KEY,
    "authId" VARCHAR(255),
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

CREATE TABLE ratings (
    "userId" INTEGER,
    "movieId" INTEGER,
    rating FLOAT,
    timestamp INTEGER,
    PRIMARY KEY ("userId", "movieId"),
    FOREIGN KEY ("movieId") REFERENCES movies("movieId"),
    FOREIGN KEY ("userId") REFERENCES users("userId")
);
