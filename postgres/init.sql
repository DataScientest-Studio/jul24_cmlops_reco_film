

CREATE TABLE IF NOT EXISTS users (
    userId SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    hached_password VARCHAR(100) NOT NULL
);

-- Charger les données à partir du fichier CSV
COPY users(userId, username, email, hached_password) FROM '/docker-entrypoint-initdb.d/users.csv' DELIMITER ',' CSV HEADER;

CREATE TABLE IF NOT EXISTS movies (
    movieId SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    genres VARCHAR(200),
    year INT
);

-- Charger les données à partir du fichier CSV
COPY movies(movieId, title, genres) FROM '/docker-entrypoint-initdb.d/processed_movies.csv' DELIMITER ',' CSV HEADER;

CREATE TABLE IF NOT EXISTS ratings (
    id SERIAL PRIMARY KEY,
    userId INT REFERENCES users(userId),
    movieId INT REFERENCES movies(movieId),
    rating FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    bayesian_mean FLOAT NOT NULL
);

-- Charger les données à partir du fichier CSV
COPY ratings(userId, movieId, rating, created_at, bayesian_mean) FROM '/docker-entrypoint-initdb.d/processed_ratings.csv' DELIMITER ',' CSV HEADER;

CREATE TABLE IF NOT EXISTS links (
    id SERIAL PRIMARY KEY,
    movieId INT REFERENCES movies(movieId),
    imdbId INT,
    tmdbId INT
);

-- Charger les données à partir du fichier CSV
COPY links(movieId, imdbId, tmdbId) FROM '/docker-entrypoint-initdb.d/processed_links.csv' DELIMITER ',' CSV HEADER;