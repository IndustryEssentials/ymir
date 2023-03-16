#!/bin/bash

set -e

# App check
curl --fail -s http://localhost:80/health
# Viewer check
curl --fail -s http://localhost:9527/health
# Auth check
curl --fail -s http://localhost:8088/health
