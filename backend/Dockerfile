FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Migrate, seed the mandatory initial data, then serve HTTP + WebSockets with Daphne.
CMD ["sh", "-c", "python manage.py migrate && python manage.py seed_initial_data && daphne -b 0.0.0.0 -p 8000 focus.asgi:application"]
