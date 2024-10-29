FROM python:3.12-slim

WORKDIR /app

COPY ./api/data /app

RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y netcat-openbsd

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"] 
