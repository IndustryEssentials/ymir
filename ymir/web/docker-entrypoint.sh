#!/usr/bin/env sh
set -eu

envsubst '${LABEL_TOOL_HOST_PORT}' < /etc/nginx/conf.d/nginx.conf.template > /etc/nginx/conf.d/nginx.conf
envsubst '${DEPLOY_MODULE_URL} ${PUBLIC_IMAGE_URL}' < /usr/share/nginx/html/config/config.js.template > /usr/share/nginx/html/config/config.js

exec "$@"
