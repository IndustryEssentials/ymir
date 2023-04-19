#!/bin/bash

# check command/proto/update_proto_py.sh for tool versions.


set -e

INPUT_DIR="./"
OUTPUT_DIR="./"

# gen protobuf py
protoc -I "$INPUT_DIR" \
      --python_out="$OUTPUT_DIR" \
      --plugin=protoc-gen-mypy=$(which protoc-gen-mypy) --mypy_out=$OUTPUT_DIR  \
      $INPUT_DIR/mir_command*.proto

touch $OUTPUT_DIR/__init__.py
