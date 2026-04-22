# AGENTS.md

## Runtime
- This repo is a single Django backend, not a monorepo. Main code lives in `api/`; Django project wiring lives in `core/`; Celery app/tasks live in `tasks/`.
- `core/urls.py` mounts `api.urls` at the root path and exposes `healthcheck/` via `django-health-check`.
- `manage.py` switches settings from `core.settings` to `core.production` only when `PRODUCTION=true`.

## Dev Workflow
- The intended local setup is Docker Compose, not ad hoc host commands: `cp .env.sample .env && docker compose up --build`.
- Compose starts four services: `django`, `celery`, `postgres`, and `redis`.
- The `django` container runs migrations on startup via `docker/web/start_server.sh`; `celery` waits for the Django health check before starting.
- For one-off Django commands, run them inside the web container: `docker compose exec django python manage.py <command>`.

## Verification
- There is no repo-owned lint, formatter, typecheck, or CI config to rely on.
- The only checked-in test module is `api/tests.py`, and it is currently just the default stub. `python manage.py test` exists but has little coverage value right now.
- The most reliable lightweight verification is `docker compose exec django python manage.py check`.

## Async Gotchas
- Session generation is asynchronous. Creating/updating a `Collection`, cloning a shared collection, or adding schedules enqueues Celery work from `api/serializers.py` and `api/views.py`.
- If the `celery` worker is not running, those writes can succeed while `Session` rows never get backfilled.
- The Celery app module is `tasks`, so the worker command is `celery -A tasks worker -l info`, not `celery -A core`.

## Domain Notes
- Attendance math lives on `api.models.Course`; session generation logic lives in `tasks/celery.py`.
- Working-day filtering is hardcoded in `api/dateutils.py`, including the holiday list. Changes to session generation often require updating that file, not just model/view code.

## Search Hygiene
- Exclude local artifacts from searches and reviews: `.venv/`, `htmlcov/`, and `**/__pycache__/` are present in this workspace and add a lot of noise.
- `bruno/` contains the checked-in Bruno API collection for manual endpoint testing.
