#!/usr/bin/env sh
set -eu

envsubst '${DEPLOY_MODULE_URL}' < /usr/share/nginx/html/config/config.js.template > /usr/share/nginx/html/config/config.js

exec "$@"
