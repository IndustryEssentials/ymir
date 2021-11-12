#!/bin/bash

set -e

IMAGE_NAME='pymir/backend_dev:latest'
docker build -f Dockerfile -t ${IMAGE_NAME} .
