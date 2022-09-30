#!/usr/bin/env sh
set -eu

envsubst '${LABEL_TOOL_HOST_URL} ${FIFTYONE_HOST_URL}' < /etc/nginx/conf.d/nginx.conf.template > /etc/nginx/conf.d/nginx.conf
envsubst '${ALGORITHM_STORE_URL}' < /usr/share/nginx/html/config/config.js.template > /usr/share/nginx/html/config/config.js

exec "$@"
