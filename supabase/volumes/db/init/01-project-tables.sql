CREATE TABLE movies (
    "movieId" SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    genres VARCHAR(255),
    year INTEGER,
    "posterUrl" VARCHAR(255),
    rating FLOAT DEFAULT 0,
    "numRatings" INTEGER DEFAULT 0,
    "lastRatingTimestamp" INTEGER,
    "imdbId" VARCHAR(10),
    "tmdbId" VARCHAR(10)
);

CREATE TABLE users (
    "userId" SERIAL PRIMARY KEY,
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

-- Fonction utilitaire pour exécuter du SQL
CREATE OR REPLACE FUNCTION exec_sql(query text)
RETURNS void AS $$
BEGIN
  EXECUTE query;
END;
$$ LANGUAGE plpgsql;

-- Fonction pour réinitialiser les séquences
CREATE OR REPLACE FUNCTION reset_all_sequences()
RETURNS void AS $$
BEGIN
  PERFORM setval(pg_get_serial_sequence('movies', 'movieId'), (SELECT MAX("movieId") FROM movies));
  PERFORM setval(pg_get_serial_sequence('users', 'userId'), (SELECT MAX("userId") FROM users));
END;
$$ LANGUAGE plpgsql;
