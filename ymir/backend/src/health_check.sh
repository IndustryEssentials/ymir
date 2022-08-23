#!/bin/bash

set -e

# App check
curl --fail -s http://localhost:80/health
# Controller check
./grpc_health_probe -addr=localhost:50066
# Viewer check
curl --fail -s http://localhost:9527/health
