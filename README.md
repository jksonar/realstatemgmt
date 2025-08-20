# Real Estate Management API

This is a comprehensive API for managing real estate properties, tenants, leases, payments, and maintenance requests. It provides a set of RESTful endpoints for interacting with the system, as well as a web interface for some functionalities.

## Features

*   **Property Management:** Create, read, update, and delete properties.
*   **Tenant Management:** Manage tenant information.
*   **Lease Management:** Create and manage leases.
*   **Payment Tracking:** Track payments, send reminders, and generate receipts.
*   **Maintenance Requests:** Manage maintenance requests for properties.
*   **Financial Reporting:** Generate financial reports and analytics.
*   **Advanced Search:** Search for properties with various filters.
*   **User Management:** User authentication and authorization.
*   **Background Tasks:** Asynchronous tasks for sending reminders and generating reports.
*   **Caching:** Caching for improved performance.
*   **Import/Export:** Import and export data in CSV format.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd RealEstateMGMT
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements/development.txt
    ```

4.  **Set up the database:**
    This project uses SQLite by default for local development. The database file `db.sqlite3` will be created automatically.

5.  **Run database migrations:**
    ```bash
    python manage.py migrate
    ```

6.  **Create a superuser:**
    ```bash
    python manage.py createsuperuser
    ```

## Usage

1.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```
    The application will be available at `http://127.0.0.1:8000/`.

2.  **Run Celery worker:**
    ```bash
    celery -A config.celery worker -l info
    ```

3.  **Run Celery beat:**
    ```bash
    celery -A config.celery beat -l info
    ```

## API Endpoints

The API endpoints are available under the `/api/` prefix.

*   `/api/token/`: Get JWT token for authentication.
*   `/api/token/refresh/`: Refresh JWT token.

### Core API

*   `/api/properties/`: Manage properties.
*   `/api/tenants/`: Manage tenants.
*   `/api/leases/`: Manage leases.
*   `/api/payments/`: Manage payments.
*   `/api/maintenance/`: Manage maintenance requests.
*   `/api/reports/`: Financial reporting.
*   `/api/outstanding-payments/`: View outstanding payments.
*   `/api/analytics/revenue/`: Revenue analytics.
*   `/api/payment-history/`: View payment history.
*   `/api/analytics/payment-methods/`: Payment method analytics.
*   `/api/dashboard/financial/`: Financial dashboard data.
*   `/api/payments/import-export/`: Import and export payments.
*   `/api/properties/import-export/`: Import and export properties.
*   `/api/properties/search/`: Search for properties.
*   `/api/saved-searches/`: Manage saved searches.
*   `/api/favorite-properties/`: Manage favorite properties.
*   `/api/search-history/`: View search history.

## Background Tasks

This project uses Celery for asynchronous tasks. The tasks are defined in `apps/core/tasks.py`.

*   `send_payment_reminders`: Send payment reminders for upcoming and overdue payments.
*   `mark_overdue_payments`: Mark payments as overdue if they are past due date.
*   `send_individual_payment_reminder`: Send a payment reminder for a specific payment.
*   `send_bulk_payment_reminders`: Send payment reminders for multiple payments.
*   `generate_monthly_payment_report`: Generate monthly payment report and send to administrators.
*   `email_financial_report`: Generate and email the financial report.

## Caching

This project uses Redis for caching. The cache is configured in `config/settings/base.py`.

## Running Tests

To run the tests, use the following command:
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

*   **Create new database migrations:**
    ```bash
    python manage.py makemigrations
    ```

*   **Open the Django shell:**
    ```bash
    python manage.py shell
    ```

*   **Open the database shell:**
    ```bash
    python manage.py dbshell
    ```

*   **Run Celery Flower for monitoring Celery tasks:**
    ```bash
    celery -A config.celery flower
    ```
