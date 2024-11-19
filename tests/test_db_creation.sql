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