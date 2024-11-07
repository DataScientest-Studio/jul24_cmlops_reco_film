Copier le .env.example de supabase/docker et le renommer en .env dans le même dossier.
Copier le .env.example de airflow et le renommer en .env dans le même dossier.
Copier le .env.example de la racine et le renommer en .env dans le même dossier.

### Dans le .env de airflow, faut :

SUPABASE_URL="http://kong:8000"
SUPABASE_KEY=(se trouve dans le .env de supabase/docker/.env)
TMDB_API_TOKEN=(que vous obtenez sur le site de TMDB)

### Dans le .env de la racine, faut :

SUPABASE_URL="http://localhost:8000"
SUPABASE_KEY=(se trouve dans le .env de supabase/docker/.env)
TMDB_API_TOKEN=(que vous obtenez sur le site de TMDB)

### Dans le .env de supabase/docker :

faut changer ENABLE_EMAIL_AUTOCONFIRM=false par ENABLE_EMAIL_AUTOCONFIRM=true

à la racine :
Exécuter "make setup-light" si vous avez deja les données brutes et que vous avez dans le dossier raw le fichier d'Antoine "links2.csv".
puis "make start" pour lancer les services.
