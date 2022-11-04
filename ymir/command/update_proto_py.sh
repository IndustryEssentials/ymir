#!/bin/bash

# Python version == 3.8.10
# protoc version == 3.13.0
# https://github.com/protocolbuffers/protobuf/releases/download/v3.13.0
# mv bin/protoc /usr/local
# mv include/google /usr/local/include/

# pip install protobuf==3.13.0
# pip install mypy-protobuf==3.0.0
# go install google.golang.org/protobuf/cmd/protoc-gen-go@v1.28.1

set -e

INPUT_DIR="./proto"
PY_OUTPUT_DIR="./mir/protos"
GO_DIR_HEL="../backend/src/ymir_hel"
rm -rf ${PY_OUTPUT_DIR}
mkdir -p ${PY_OUTPUT_DIR}

# gen protobuf py
protoc -I "${INPUT_DIR}" \
      --python_out="${PY_OUTPUT_DIR}" \
      --go_out="${GO_DIR_HEL}" \
      --plugin=protoc-gen-mypy=$(which protoc-gen-mypy) --mypy_out=${PY_OUTPUT_DIR}  \
      "$INPUT_DIR/mir_command.proto"

touch ${PY_OUTPUT_DIR}/__init__.py
