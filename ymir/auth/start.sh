#! /usr/bin/env sh

set -e

APP_MODULE="auth.main:app"

GUNICORN_CONF="auth/gunicorn_conf.py"

WORKER_CLASS="uvicorn.workers.UvicornWorker"

exec gunicorn -w 1 -k "$WORKER_CLASS" -c "$GUNICORN_CONF" "$APP_MODULE"
