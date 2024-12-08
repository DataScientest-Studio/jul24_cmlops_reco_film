# Use the official Python slim image
FROM python:3.8-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY ./requirements.txt ./requirements.txt

COPY ./data_to_db.py ./data_to_db.py

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "data_to_db.py"]