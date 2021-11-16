#!/bin/bash

set -e

EXECUTOR_TRAINING='industryessentials/executor-det-yolov4-training'
EXECUTOR_MINING='industryessentials/executor-det-yolov4-mining'

stop() {
docker-compose down
}

pre_start() {
docker pull ${EXECUTOR_TRAINING}
docker pull ${EXECUTOR_MINING}
docker-compose pull
stop
}

start() {
pre_start
docker-compose up -d
}

print_help() {
    printf '\nUsage: \n  sh ymir.sh start/stop.\n'
}

# main
main() {
    if [[ $# -eq 0 ]]; then
        print_help
    else
        $1
    fi
}

printf 'Welcome to Ymir world.\n'
main "$@"
