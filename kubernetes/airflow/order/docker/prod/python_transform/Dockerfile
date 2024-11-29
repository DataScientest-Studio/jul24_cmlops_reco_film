FROM python:3.8-slim

WORKDIR /app

COPY ./build_features.py ./build_features.py

COPY ./requirements.txt ./requirements.txt

RUN mkdir -p data/to_ingest

RUN pip install -r requirements.txt
