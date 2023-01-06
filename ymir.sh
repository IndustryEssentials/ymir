#!/bin/bash

set -e

DOCKER_BACKEND='industryessentials/ymir-backend'
DOCKER_WEB='industryessentials/ymir-web'

DEV_SOURCE_BACKEND_PIP='https://pypi.mirrors.ustc.edu.cn/simple'
DEV_SOURCE_WEB_NPM='https://registry.npmmirror.com'

FIELD_LABEL_TOOL='LABEL_TOOL'
FIELD_LABEL_TOOL_LS='label_studio'
FIELD_LABEL_TOOL_LF='label_free'
ENV_FILE='.env'
FIELD_SERVER_RUNTIME='SERVER_RUNTIME'
FIELD_DEPLOY_MODULE_HOST_PORT='DEPLOY_MODULE_HOST_PORT'

check_docker_compose_version() {
    MIN_DC_VER="1.29.2"
    if ! command -v docker-compose &> /dev/null; then
        echo "please install docker-compose ${MIN_DC_VER} or newer version."
        exit
    fi
    if ! echo "$(docker-compose version --short) ${MIN_DC_VER}" | tr " " "\n" | sort -V | head -n 1 | grep -Eq "^${MIN_DC_VER}$"; then
        echo "please upgrade docker-compose to ${MIN_DC_VER} or newer version."
        exit
    fi
}

check_docker_version() {
    MIN_DOCKER_VER="20.10"
    if ! command -v docker &> /dev/null; then
        echo "please install docker ${MIN_DOCKER_VER} or newer version."
        exit
    fi
    if ! echo "$(docker version --format '{{.Client.Version}}') ${MIN_DOCKER_VER}" | tr " " "\n" | sort -V | head -n 1 | grep -Eq "^${MIN_DOCKER_VER}$"; then
        echo "please upgrade docker to ${MIN_DOCKER_VER} or newer version."
        exit
    fi
}

has_nvidia_driver(){
    if ! command -v nvidia-smi &> /dev/null; then
        return 1
    fi
    if [ $(nvidia-smi -L | grep UUID:| wc -l) -eq 0 ]; then
        return 1
    fi
    return 0
}

check_server_runtime(){
    if cat ${ENV_FILE} | grep -oE "^${FIELD_SERVER_RUNTIME}=nvidia$"; then
        if ! has_nvidia_driver; then
            echo "please make sure Nvidia driver is installed when server runtime is set to nvidia."
            exit
        fi
    fi
}

stop() {
docker-compose -f docker-compose.yml -f docker-compose.dev.yml -f docker-compose.label_studio.yml \
-f docker-compose.labelfree.yml -f docker-compose.modeldeploy.yml down
}

pre_start() {
stop
}

set_label_tool() {
if ! cat ${ENV_FILE} | grep "${FIELD_LABEL_TOOL}=$"; then
    echo "label_tool already set"
    return
fi

cat <<- EOF
Which label-tool would you like to start (1/2/3)?
1.Label Studio
2.Label Free
3.None

EOF

while true; do
    read -p "You choose (1/2/3)?" yn
    case $yn in
        [1]* ) sed -i.bk "s/^${FIELD_LABEL_TOOL}=.*/${FIELD_LABEL_TOOL}=${FIELD_LABEL_TOOL_LS}/" ${ENV_FILE} && rm -f ${ENV_FILE}.bk; break;;
        [2]* ) sed -i.bk "s/^${FIELD_LABEL_TOOL}=.*/${FIELD_LABEL_TOOL}=${FIELD_LABEL_TOOL_LF}/" ${ENV_FILE} && rm -f ${ENV_FILE}.bk; break;;
        [3]* ) break;;
        * ) echo "Please answer 1/2/3.";;
    esac
done
}

start_label_tool() {
if cat ${ENV_FILE} | grep "${FIELD_LABEL_TOOL}=$"; then
    echo "no label_tool set, skip."
    return
fi

if cat ${ENV_FILE} | grep "${FIELD_LABEL_TOOL}=${FIELD_LABEL_TOOL_LS}"; then
    echo "label-studio set, starting..."
    docker-compose -f docker-compose.label_studio.yml up -d
    return
elif cat ${ENV_FILE} | grep "${FIELD_LABEL_TOOL}=${FIELD_LABEL_TOOL_LF}"; then
    echo "label-free set, starting..."
    docker-compose -f docker-compose.labelfree.yml up -d
    return
else
    echo "unsupported label tool"
    exit
fi
}

start_deploy_module() {
    if cat ${ENV_FILE} | grep -oE "^${FIELD_DEPLOY_MODULE_HOST_PORT}=$"; then
        echo "DEPLOY_MODULE_HOST_PORT not set, skip deploy module startup"
        return
    fi

    if ! cat ${ENV_FILE} | grep -oE "^${FIELD_DEPLOY_MODULE_HOST_PORT}=[0-9]{1,5}$"; then
        echo "DEPLOY_MODULE_HOST_PORT is invalid"
        exit
    fi

    echo "deploy module, starting..."
    docker-compose -f docker-compose.modeldeploy.yml up -d
}

start() {
check_docker_version
check_docker_compose_version
check_server_runtime
pre_start

start_deploy_module

if [[ $1 == 'dev' ]]; then
    printf '\nin dev mode, building images.\n'
    docker build \
        -t ${DOCKER_BACKEND} \
        --build-arg PIP_SOURCE=${DEV_SOURCE_BACKEND_PIP} \
        git@github.com:IndustryEssentials/ymir.git#dev:/ymir -f Dockerfile.backend
    docker build \
        -t ${DOCKER_WEB} \
        --build-arg NPM_REGISTRY=${DEV_SOURCE_WEB_NPM} \
        git@github.com:IndustryEssentials/ymir.git#dev:/ymir/web
    sed -i.bk "s/^${FIELD_UUID}=.*$/${FIELD_UUID}=testdev/" ${ENV_FILE} && rm -f *.bk
else
    printf '\nin prod mode, starting service.\n'
fi

set_label_tool
docker-compose up -d
start_label_tool
}

update() {
    stop

cat <<- EOF
Before proceed, make sure to BACKUP your YMIR-workplace folder.
Only supports to upgrade from 1.1.0 (22-May) to 2.0.0 (22-Oct), otherwise may cause data damage.
EOF

while true; do
    read -p "Continue (y/n)?" yn
    case $yn in
        [Yy]* ) docker-compose -f docker-compose.updater.yml up; break;;
        * ) break;;
    esac
done
}

print_help() {
    printf '\nUsage: \n  bash ymir.sh start/stop/update.\n'
}

# main
main() {
    if [ "$EUID" -eq 0 ]
        then echo "Error: using sudo, this will cause permission issue."
        exit
    fi

    if [[ $# -eq 0 ]]; then
        print_help
    else
        "$@"
    fi
}

printf 'Welcome to Ymir world.\n'
main "$@"
