#!/bin/bash

# Python version == 3.8.10
# protoc version == 3.13.0
# https://github.com/protocolbuffers/protobuf/releases/download/v3.14.0
# mv bin/protoc /usr/local
# mv include/google /usr/local/include/

# pip install protobuf==3.13.0
# pip install mypy-protobuf==3.0.0
# protoc-gen-go 1.28.1

set -e

INPUT_DIR="./proto"
OUTPUT_DIR="./mir/protos"
VIEWER_GO_DIR="../backend/src/ymir_viewer/common"
rm -rf $OUTPUT_DIR
mkdir -p $OUTPUT_DIR

# gen protobuf py
protoc -I "$INPUT_DIR" \
      --python_out="$OUTPUT_DIR" \
      --go_out="$VIEWER_GO_DIR" \
      --plugin=protoc-gen-mypy=$(which protoc-gen-mypy) --mypy_out=$OUTPUT_DIR  \
      "$INPUT_DIR/mir_command.proto"

touch $OUTPUT_DIR/__init__.py
