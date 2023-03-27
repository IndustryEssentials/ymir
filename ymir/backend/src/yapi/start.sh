#! /usr/bin/env sh

set -e

APP_MODULE="yapi.main:app"

GUNICORN_CONF="yapi/gunicorn_conf.py"

WORKER_CLASS="uvicorn.workers.UvicornWorker"

exec gunicorn -w 1 -k "$WORKER_CLASS" -c "$GUNICORN_CONF" "$APP_MODULE"
