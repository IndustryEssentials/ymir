#!/usr/bin/env sh
set -eu

envsubst '${LABEL_STUDIO_OPEN_HOST} ${LABEL_STUDIO_OPEN_PORT}' < /etc/nginx/conf.d/nginx.conf.template > /etc/nginx/conf.d/nginx.conf

exec "$@"
