#!/bin/bash

set -e

EXECUTOR_TRAINING='industryessentials/executor-det-yolov4-training'
EXECUTOR_MINING='industryessentials/executor-det-yolov4-mining'

DOCKER_BACKEND='industryessentials/ymir-backend'
DOCKER_WEB='industryessentials/ymir-web'

DEV_SOURCE_BACKEND_PIP='https://pypi.mirrors.ustc.edu.cn/simple'
DEV_SOURCE_WEB_NPM='https://registry.npmmirror.com'

FIELD_ALLOW_FEEDBACK='ALLOW_ANONYMOUS_FEEDBACK'
FIELD_UUID='ANONYMOUS_UUID'
ENV_FILE='.env'

stop() {
docker-compose down
docker-compose -f docker-compose.label.yml down
}

pre_start() {
docker pull ${EXECUTOR_TRAINING}
docker pull ${EXECUTOR_MINING}
stop
}

choose_yes () {
sed -i.bk "s/^${FIELD_ALLOW_FEEDBACK}=.*/${FIELD_ALLOW_FEEDBACK}=True/" ${ENV_FILE} && rm -f *.bk

uuid=$(uuidgen)
sed -i.bk "s/^${FIELD_UUID}=$/${FIELD_UUID}=${uuid}/" .env && rm -f *.bk
}

choose_no () {
sed -i.bk "s/^${FIELD_ALLOW_FEEDBACK}=.*/${FIELD_ALLOW_FEEDBACK}=False/" ${ENV_FILE} && rm -f *.bk
}

check_permission() {
cat <<- EOF
Would you allow YMIR to send us automatic reports helps us prioritize what to fix and improve in YMIR?
These reports can include things like task type, how much resources you’re using. NO personal information collected.
EOF

while true; do
    read -p "You choose (Y/n)?" yn
    case $yn in
        [Yy]*|'' ) choose_yes; break;;
        [Nn]* ) choose_no; break;;
        * ) echo "Please answer (y)es or (n)o.";;
    esac
done
}

start_label_free () {
docker-compose -f docker-compose.label.yml up -d
}

label_free() {
cat <<- EOF
Would you like to start LabelFree?
EOF

while true; do
    read -p "You choose (Y/n)?" yn
    case $yn in
        [Yy]*|'' ) start_label_free; break;;
        [Nn]* ) break;;
        * ) echo "Please answer (y)es or (n)o.";;
    esac
done
}

start() {
check_permission
pre_start

if [[ $1 == 'dev' ]]; then
    printf '\nin dev mode, building images.\n'
    docker build \
        -t ${DOCKER_BACKEND} \
        --build-arg PIP_SOURCE=${DEV_SOURCE_BACKEND_PIP} \
        --build-arg SERVER_MODE='dev' \
        git@github.com:IndustryEssentials/ymir.git#dev:/ymir -f Dockerfile.backend
    docker build \
        -t ${DOCKER_WEB} \
        --build-arg NPM_REGISTRY=${DEV_SOURCE_WEB_NPM} \
        git@github.com:IndustryEssentials/ymir.git#dev:/ymir/web
    sed -i.bk "s/^${FIELD_UUID}=.*$/${FIELD_UUID}=testdev/" .env && rm -f *.bk
else
    printf '\nin prod mode, pulling images.\n'
    docker-compose pull
fi
label_free
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
        "$@"
    fi
}

printf 'Welcome to Ymir world.\n'
main "$@"
