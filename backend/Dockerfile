# Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Системные зависимости для psycopg2 и geoalchemy2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    gdal-bin \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 300 --retries 5 -r requirements.txt

COPY . .
