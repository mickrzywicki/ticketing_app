# Helpdesk

A ticketing system built as a set of services:

| Service | Stack | Status |
|---|---|---|
| `services/core` | Python 3.13, Django, Django REST Framework, PostgreSQL, JWT | in progress |
| `services/notifier` | Flask, Redis | planned |

## Local development

```bash
docker compose up -d db redis          # Postgres on localhost:5433, Redis on 6379

cd services/core
cp .env.example .env
uv sync
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

- API docs (Swagger): http://localhost:8000/api/docs/
- Admin: http://localhost:8000/admin/

Or run everything in containers: `docker compose up --build`.

## Quality checks

```bash
cd services/core
uv run ruff check . && uv run ruff format --check .
uv run mypy .
uv run pytest
```

The same checks run in GitHub Actions (`.github/workflows/ci.yml`).
