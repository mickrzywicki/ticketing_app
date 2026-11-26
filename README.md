# Helpdesk

[![CI](https://github.com/mickrzywicki/ticketing_app/actions/workflows/ci.yml/badge.svg)](https://github.com/mickrzywicki/ticketing_app/actions/workflows/ci.yml)

A ticketing system built as a set of services:

| Service | Stack | Status |
|---|---|---|
| `services/core` | Python 3.13, Django, Django REST Framework, PostgreSQL, JWT, Celery | in progress |
| `services/notifier` | Python 3.13, Flask, Gunicorn | in progress |

```
core (Django API) ──► Redis ──► worker (Celery) ──HTTP──► notifier (Flask)
        │
        └── PostgreSQL
```

## Local development

Run everything in containers:

```bash
docker compose up --build
```

Or run services on the host, with only Postgres and Redis in Docker:

```bash
docker compose up -d db redis          # Postgres on localhost:5433, Redis on 6379

# core API
cd services/core
cp .env.example .env
uv sync
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver

# Celery worker (second terminal, services/core)
uv run celery -A config worker -l info

# notifier (third terminal)
cd services/notifier
uv sync
uv run flask --app notifier run --port 5001
```

- API docs (Swagger): http://localhost:8000/api/docs/
- Admin: http://localhost:8000/admin/
- Notifier health check: http://localhost:5001/health

## Quality checks

In each service directory (`services/core`, `services/notifier`):

```bash
uv run ruff check . && uv run ruff format --check .
uv run mypy .
uv run pytest
```

The same checks run in GitHub Actions (`.github/workflows/ci.yml`).
