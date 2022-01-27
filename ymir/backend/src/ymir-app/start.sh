#! /usr/bin/env sh

set -e

APP_MODULE="app.main:app"

GUNICORN_CONF="app/gunicorn_conf.py"

WORKER_CLASS="uvicorn.workers.UvicornWorker"

exec gunicorn -k "$WORKER_CLASS" -c "$GUNICORN_CONF" "$APP_MODULE"
