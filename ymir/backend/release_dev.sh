#!/bin/bash

set -e

IMAGE_NAME='pymir/backend_dev:latest'
docker build --no-cache -f Dockerfile-dev -t ${IMAGE_NAME} .
