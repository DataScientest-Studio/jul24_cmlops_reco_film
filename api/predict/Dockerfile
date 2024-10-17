
FROM python:3.12-slim

WORKDIR /app

COPY ./api/predict /app/predict

COPY ./models /app/models

RUN pip install --no-cache-dir -r predict/requirements.txt

EXPOSE 8000

# TODO remove --reload for production
CMD ["uvicorn", "predict.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 
