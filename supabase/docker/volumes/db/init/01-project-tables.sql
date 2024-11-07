CREATE TABLE movies (
    "movieId" INTEGER PRIMARY KEY,
    "title" VARCHAR(255) NOT NULL,
    "genres" VARCHAR(255),
    "year" INTEGER,
);

CREATE TABLE links (
    "movieId" INTEGER PRIMARY KEY,
    "imdbId" VARCHAR(10),
    "tmdbId" VARCHAR(10),
    FOREIGN KEY ("movieId") REFERENCES movies("movieId")
);

CREATE TABLE ratings (
    "userId" INTEGER,
    "movieId" INTEGER,
    "rating" FLOAT,
    "timestamp" INTEGER,
    "bayesian_mean" FLOAT,
    PRIMARY KEY ("userId", "movieId"),
    FOREIGN KEY ("movieId") REFERENCES movies("movieId"),
    FOREIGN KEY ("userId") REFERENCES users("userId")
);
