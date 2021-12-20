#!/bin/bash

set -e

# IMAGE_NAME='pymir/backend_dev:latest'
IMAGE_NAME="zzw-backend:test"
docker build -f Dockerfile-dev -t ${IMAGE_NAME} .
