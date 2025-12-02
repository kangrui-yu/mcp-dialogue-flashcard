FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY gunicorn.conf.py ./gunicorn.conf.py
ENV APP_HOST=0.0.0.0
ENV APP_PORT=8081

EXPOSE 8081
CMD ["gunicorn", "-c", "gunicorn.conf.py", "app.wsgi:app"]