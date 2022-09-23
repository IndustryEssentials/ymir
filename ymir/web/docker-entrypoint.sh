#!/usr/bin/env sh
set -eu

envsubst '${LABEL_TOOL_HOST_URL} ${FIFTYONE_HOST_URL} ${ALGO_STORE_URL}' < /etc/nginx/conf.d/nginx.conf.template > /etc/nginx/conf.d/nginx.conf

exec "$@"
