# Use the official Python slim image
FROM python:3.8-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY ./requirements.txt ./requirements.txt

# Install necessary system packages and Python dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    apt-get remove --purge -y gcc libpq-dev && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Copy your application files
COPY ./build_features.py ./build_features.py
COPY ./data_to_db.py ./data_to_db.py
COPY ./start.sh ./start.sh

# Make start.sh executable
RUN chmod +x start.sh

# Command to run your application (if applicable)
CMD ["./start.sh"]