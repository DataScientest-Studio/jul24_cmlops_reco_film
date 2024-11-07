
FROM python:3.12-slim

WORKDIR /app

COPY ./api/predict /app

COPY ./ml/models /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# TODO remove --reload for production
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002", "--reload"] 
