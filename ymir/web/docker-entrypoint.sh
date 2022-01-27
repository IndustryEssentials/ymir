#!/usr/bin/env sh
set -eu

envsubst '${LABEL_TOOL_URL}' < /etc/nginx/conf.d/nginx.conf.template > /etc/nginx/conf.d/nginx.conf

exec "$@"
