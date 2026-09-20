# Real Estate Management (EstateFlow)

A Django-based platform for managing real estate properties, tenants, leases, rent payments, maintenance requests, and sales leads. It exposes both a server-rendered web UI (Bootstrap) and a REST API (Django REST Framework + JWT auth), backed by Celery for background jobs and Redis for caching.

## Features

* **Property Management** — create, read, update, and delete properties.
* **Tenant Management** — manage tenant information and documents.
* **Lease Management** — create and manage lease agreements.
* **Payment Tracking** — track rent payments, send reminders, generate receipts.
* **Maintenance Requests** — manage maintenance requests for properties.
* **Lead Management** — capture and track sales/rental leads.
* **Financial Reporting** — generate financial reports and analytics.
* **Advanced Search** — search properties with saved/advanced filters.
* **User Management** — authentication and role-based authorization.
* **Background Tasks** — async jobs (reminders, reports) via Celery.
* **Caching** — Redis-backed cache.
* **Import/Export** — import and export data in CSV format.

## Tech Stack

| Layer        | Technology |
|--------------|------------|
| Backend      | Python 3.11+, Django 5.2, Django REST Framework |
| Auth         | `djangorestframework-simplejwt` (API), Django session auth (web UI) |
| Database     | SQLite (local/dev), PostgreSQL (docker/production) |
| Cache/Queue  | Redis, Celery (+ Celery Beat for scheduled tasks) |
| Frontend     | Django templates, Bootstrap 5, Bootstrap Icons |
| Static files | WhiteNoise (in the Docker image) |
| PDF/Exports  | xhtml2pdf, reportlab, openpyxl, pandas |

## Project Structure

```
config/
  settings/
    base.py          # shared settings
    local.py          # ENVIRONMENT=local      -> sqlite (db.local.sqlite3)
    development.py     # ENVIRONMENT=development -> sqlite (db.development.sqlite3) [default]
    uat.py             # ENVIRONMENT=uat         -> sqlite (db.uat.sqlite3)
    production.py       # ENVIRONMENT=production  -> PostgreSQL (env-driven)
    docker.py           # used inside the Docker image -> PostgreSQL (env-driven) + WhiteNoise
  urls.py, wsgi.py, asgi.py, celery.py
apps/
  core/          # shared utilities, middleware, dashboard-adjacent helpers
  accounts/      # custom user model, auth views
  dashboard/     # dashboard views
  properties/    # property CRUD, search
  tenants/       # tenant management
  leases/        # lease management
  payments/      # payments, receipts, financial reports
  maintenance/   # maintenance requests
  leads/         # lead capture/tracking (API + frontend)
  reports/       # reporting views
templates/       # Bootstrap-based server-rendered templates
static/          # source static assets
requirements/    # per-environment pip requirements
```

## Environment Configuration

Django picks its settings module via the `ENVIRONMENT` variable, resolved in [config/settings/__init__.py](config/settings/__init__.py):

| `ENVIRONMENT` value | Settings module                | Database |
|----------------------|--------------------------------|----------|
| *(unset)*, `development` | `config.settings.development` | SQLite (`db.development.sqlite3`) |
| `local`               | `config.settings.local`        | SQLite (`db.local.sqlite3`) |
| `uat`                 | `config.settings.uat`          | SQLite (`db.uat.sqlite3`) |
| `production`          | `config.settings.production`   | PostgreSQL (env vars) |
| *(set by Docker image)* | `config.settings.docker`     | PostgreSQL (env vars) |

`manage.py` / `wsgi.py` default `DJANGO_SETTINGS_MODULE` to `config.settings.development`; override it directly (as the Docker image does) to target a different environment.

Copy [.env.example](.env.example) to `.env` for local (non-Docker) development:

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True`/`False` |
| `ALLOWED_HOSTS` | Comma-separated hostnames |
| `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | Only used by `production`/`docker` settings |
| `REDIS_HOST`, `REDIS_PORT` | Redis connection for cache/Celery |
| `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | SMTP credentials |

## Local Development (without Docker)

1. **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd realstatemgmt
    ```

2. **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install dependencies:**
    ```bash
    pip install -r requirements/base.txt
    ```

4. **Configure environment variables:**
    ```bash
    cp .env.example .env
    ```
    The default settings use SQLite, so no database server is required.

5. **Run database migrations:**
    ```bash
    python manage.py migrate
    ```

6. **Create a superuser:**
    ```bash
    python manage.py createsuperuser
    ```

7. **Run the development server:**
    ```bash
    python manage.py runserver
    ```
    The application will be available at `http://127.0.0.1:8000/`.

8. **(Optional) Run Celery worker / beat** — requires a running Redis instance:
    ```bash
    celery -A config.celery worker -l info
    celery -A config.celery beat -l info
    ```

## Running with Docker

The Docker setup runs two services: a Django app server (`web`, via Gunicorn) and a PostgreSQL database (`db`).

**Files:** [Dockerfile](Dockerfile), [docker-compose.yml](docker-compose.yml), [entrypoint.sh](entrypoint.sh), [config/settings/docker.py](config/settings/docker.py).

1. **Copy the Docker env template:**
    ```bash
    cp .env.docker.example .env.docker
    ```
    Adjust `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, etc. as needed. `DB_NAME` / `DB_USER` / `DB_PASSWORD` must match the `db` service's `POSTGRES_*` values in `docker-compose.yml` (both default to `realstatemgmt`).

2. **Build and start the stack:**
    ```bash
    docker compose --env-file .env.docker up --build
    ```
    On startup, the `web` container automatically waits for Postgres, runs `migrate`, runs `collectstatic`, then starts Gunicorn.

3. **Access the app** at `http://localhost:8000/`. PostgreSQL is also exposed on `localhost:5432`.

4. **Create a superuser inside the container:**
    ```bash
    docker compose --env-file .env.docker exec web python manage.py createsuperuser
    ```

5. **View logs / stop the stack:**
    ```bash
    docker compose --env-file .env.docker logs -f web
    docker compose --env-file .env.docker down          # stop (keeps data volumes)
    docker compose --env-file .env.docker down -v        # stop and wipe Postgres/static/media data
    ```

**Note:** Redis/Celery are referenced in the app's settings but are **not** included as Docker services. If you need working cache/Celery inside Docker, add a `redis` service and point `REDIS_HOST`/`CELERY_BROKER_URL` at it.

## API Endpoints

The API endpoints are available under the `/api/` prefix.

* `/api/token/`: Get JWT token for authentication.
* `/api/token/refresh/`: Refresh JWT token.

### Core API

* `/api/properties/`: Manage properties.
* `/api/tenants/`: Manage tenants.
* `/api/leases/`: Manage leases.
* `/api/payments/`: Manage payments.
* `/api/maintenance/`: Manage maintenance requests.
* `/api/reports/`: Financial reporting.
* `/api/outstanding-payments/`: View outstanding payments.
* `/api/analytics/revenue/`: Revenue analytics.
* `/api/payment-history/`: View payment history.
* `/api/analytics/payment-methods/`: Payment method analytics.
* `/api/dashboard/financial/`: Financial dashboard data.
* `/api/payments/import-export/`: Import and export payments.
* `/api/properties/import-export/`: Import and export properties.
* `/api/properties/search/`: Search for properties.
* `/api/saved-searches/`: Manage saved searches.
* `/api/favorite-properties/`: Manage favorite properties.
* `/api/search-history/`: View search history.
* `/api/leads/`: Manage leads.

### Web UI Routes

* `/dashboard/`: Dashboard.
* `/properties/`, `/tenants/`, `/leases/`, `/payments/`, `/maintenance/`, `/reports/`, `/leads/`: List/detail/form views.
* `/accounts/`: Login, registration, profile.
* `/admin/`: Django admin.

## Background Tasks

This project uses Celery for asynchronous tasks. The tasks are defined in `apps/core/tasks.py`.

* `send_payment_reminders`: Send payment reminders for upcoming and overdue payments.
* `mark_overdue_payments`: Mark payments as overdue if they are past due date.
* `send_individual_payment_reminder`: Send a payment reminder for a specific payment.
* `send_bulk_payment_reminders`: Send payment reminders for multiple payments.
* `generate_monthly_payment_report`: Generate monthly payment report and send to administrators.
* `email_financial_report`: Generate and email the financial report.

## Caching

This project uses Redis for caching. The cache is configured in `config/settings/base.py`.

## Running Tests

```bash
python manage.py test
```

## Code Style and Linting

This project uses `black` for code formatting and `flake8` for linting.

**Install the tools:**
```bash
pip install black flake8
```

**Format the code:**
```bash
black .
```

**Run the linter:**
```bash
flake8 .
```

## Running Tests with Coverage

This project uses `coverage` to measure code coverage.

**Install the tool:**
```bash
pip install coverage
```

**Run tests with coverage:**
```bash
coverage run manage.py test
```

**View the coverage report:**
```bash
coverage report
```

**Generate an HTML report:**
```bash
coverage html
```
The report will be generated in the `htmlcov` directory.

## Other Useful Commands

* **Create new database migrations:**
    ```bash
    python manage.py makemigrations
    ```

* **Open the Django shell:**
    ```bash
    python manage.py shell
    ```

* **Open the database shell:**
    ```bash
    python manage.py dbshell
    ```

* **Run Celery Flower for monitoring Celery tasks:**
    ```bash
    celery -A config.celery flower
    ```
