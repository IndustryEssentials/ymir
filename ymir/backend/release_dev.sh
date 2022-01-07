#!/bin/bash

set -e

IMAGE_NAME='ymir/backend_dev:latest'
docker build -f Dockerfile-dev -t ${IMAGE_NAME} .
