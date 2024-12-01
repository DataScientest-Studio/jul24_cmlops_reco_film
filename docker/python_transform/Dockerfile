FROM python:3.8-slim

WORKDIR /app

COPY ./build_features.py ./build_features.py

COPY ./data_to_db.py ./data_to_db.py

COPY ./start.sh ./start.sh

COPY ./requirements.txt ./requirements.txt

RUN mkdir -p data/to_ingest

RUN pip install -r requirements.txt

# Rendre le script start.sh exécutable
RUN chmod +x start.sh

# Spécifier la commande à exécuter lors du démarrage du conteneur
CMD ["./start.sh"]