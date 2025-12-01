# src/python_api/Dockerfile
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# System deps (if you need more, add here)
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY app ./app
COPY gunicorn.conf.py ./gunicorn.conf.py

# Default env for container
ENV APP_HOST=0.0.0.0
ENV APP_PORT=8081

# Expose port for debug / local access
EXPOSE 8081

# Run with Gunicorn (prod-ish)
CMD ["gunicorn", "-c", "gunicorn.conf.py", "app.wsgi:app"]