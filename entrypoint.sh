#!/bin/sh
set -e

python <<'END'
import os
import sys
import time

import psycopg2

host = os.environ.get("DB_HOST", "db")
port = os.environ.get("DB_PORT", "5432")
user = os.environ.get("DB_USER", "postgres")
password = os.environ.get("DB_PASSWORD", "")
dbname = os.environ.get("DB_NAME", "postgres")

for attempt in range(1, 31):
    try:
        psycopg2.connect(
            host=host, port=port, user=user, password=password, dbname=dbname
        ).close()
        break
    except psycopg2.OperationalError as exc:
        print(f"Waiting for database at {host}:{port} ({attempt}/30)... {exc}")
        time.sleep(1)
else:
    sys.exit("Database never became available, exiting.")
END

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec "$@"
