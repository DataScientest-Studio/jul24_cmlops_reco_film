CREATE TABLE movies (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    genre VARCHAR(255) NOT NULL
);

CREATE TABLE ratings (
    id SERIAL PRIMARY KEY,
    movie_id INT REFERENCES movies(id),
    rating INT NOT NULL
);

CREATE TABLE links (
    id SERIAL PRIMARY KEY,
    movie_id INT REFERENCES movies(id),
    url VARCHAR(255) NOT NULL
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL
);

SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public';

SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'movies';

SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'ratings';

SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'links';

SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'users';