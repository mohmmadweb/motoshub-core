FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

# postgresql-client supplies pg_dump for the console's manual backup; the image
# libraries are what Pillow needs to write JPEG/PNG thumbnails.
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential libpq-dev postgresql-client \
        libjpeg-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/media /app/staticfiles /app/backups \
 && adduser --disabled-password --gecos "" appuser \
 && chown -R appuser /app
USER appuser

EXPOSE 8000
ENTRYPOINT ["./docker/entrypoint.sh"]
CMD ["web"]
