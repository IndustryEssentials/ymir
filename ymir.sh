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
FIELD_LABEL_TOOL='LABEL_TOOL'
FIELD_LABEL_TOOL_HOST_IP='LABEL_TOOL_HOST_IP'
FIELD_LABEL_TOOL_TOKEN='LABEL_TOOL_TOKEN'
FIELD_LABEL_TOOL_LS='label_studio'
FIELD_LABEL_TOOL_LF='label_free'
ENV_FILE='.env'

stop() {
docker-compose down
docker-compose -f docker-compose.label_studio.yml down
docker-compose -f docker-compose.labelfree.yml down
}

pre_start() {
docker pull ${EXECUTOR_TRAINING}
docker pull ${EXECUTOR_MINING}
stop
}

choose_yes () {
sed -i.bk "s/^${FIELD_ALLOW_FEEDBACK}=.*/${FIELD_ALLOW_FEEDBACK}=True/" ${ENV_FILE} && rm -f ${ENV_FILE}.bk

uuid=$(uuidgen)
sed -i.bk "s/^${FIELD_UUID}=$/${FIELD_UUID}=${uuid}/" ${ENV_FILE} && rm -f *.bk
}

choose_no () {
sed -i.bk "s/^${FIELD_ALLOW_FEEDBACK}=.*/${FIELD_ALLOW_FEEDBACK}=False/" ${ENV_FILE} && rm -f ${ENV_FILE}.bk
}

check_permission() {
if ! cat ${ENV_FILE} | grep "${FIELD_ALLOW_FEEDBACK}=$"; then
    echo "permission already set"
    return
fi

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

set_label_tool() {
if ! cat ${ENV_FILE} | grep "${FIELD_LABEL_TOOL}=$"; then
    echo "label_tool already set"
    return
fi

cat <<- EOF
Before proceed, make sure to set LABEL_TOOL_HOST_IP, LABEL_TOOL_HOST_PORT, LABEL_TOOL_TOKEN fields as needed.
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
set_label_tool
if cat ${ENV_FILE} | grep "${FIELD_LABEL_TOOL}=$"; then
    echo "no label_tool set, skip."
    return
fi

# check label tool ip address.
if ! cat ${ENV_FILE} | grep -oE "${FIELD_LABEL_TOOL_HOST_IP}=http://\b([0-9]{1,3}\.){3}[0-9]{1,3}\b"; then
    echo "Label tool's IP is not set, expected format: http://xxx.xxx.xxx.xxx"
    exit
fi

if cat ${ENV_FILE} | grep "${FIELD_LABEL_TOOL}=${FIELD_LABEL_TOOL_LS}"; then
    echo "label-studio set, starting..."
    if ! cat ${ENV_FILE} | grep -oE "${FIELD_LABEL_TOOL_TOKEN}=\"Token \b[0-9a-z]{40}\b\""; then
        echo "Label studio's token is not set, expected format: Token xxxxx..."
        exit
    fi
    docker-compose -f docker-compose.label_studio.yml up -d
    return
elif cat ${ENV_FILE} | grep "${FIELD_LABEL_TOOL}=${FIELD_LABEL_TOOL_LF}"; then
    if ! cat ${ENV_FILE} | grep -oE "${FIELD_LABEL_TOOL_TOKEN}=\"Bearer "; then
        echo "Label free's token is not set, expected format: Bearer xxxxx..."
        exit
    fi
    echo "label-free set, starting..."
    docker-compose -f docker-compose.labelfree.yml up -d
    return
else
    echo "unsupported label tool"
    exit
fi
}

start() {
check_permission
pre_start

start_label_tool

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
docker-compose up -d
}

print_help() {
    printf '\nUsage: \n  bash ymir.sh start/stop.\n'
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
