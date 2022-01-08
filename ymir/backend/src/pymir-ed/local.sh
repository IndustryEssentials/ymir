#! /bin/bash

# for event dispatcher local test
export ED_REDIS_URI='redis://'
export API_KEY_SECRET='36fbc9d3c0ce04dae75389d5b48e3fa8424c'

uvicorn main:app_ed --host 192.168.28.38 --port 8090
