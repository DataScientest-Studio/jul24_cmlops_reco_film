- API TMDB : https://www.themoviedb.org/documentation/api
  Si vous en avez besoin je peux vous filer la mienne mais ça prend 2min de la demander.
  Faut la dans le .env de la racine et dans le .env de airflow.

### Dans le .env de airflow, faut :

SUPABASE_URL="http://kong:8000"
SUPABASE_KEY=(se trouve dans le .env de supabase/docker/.env)
TMDB_API_TOKEN=

### Dans le .env de la racine, faut :

SUPABASE_URL="http://localhost:8000"
SUPABASE_KEY=(se trouve dans le .env de supabase/docker/.env)
TMDB_API_TOKEN=

### Dans le .env de supabase/docker :

faut changer ENABLE_EMAIL_AUTOCONFIRM=false par ENABLE_EMAIL_AUTOCONFIRM=true

à la racine :
Exécuter "make setup-light" si vous avez deja les données brutes et que vous avez dans le dossier raw le fichier d'Antoine "links2.csv".
puis "make start" pour lancer les services.
puis "make clean-db" pour load les données dans la db.
