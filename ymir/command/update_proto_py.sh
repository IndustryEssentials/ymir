#!/bin/bash

# Python version >= 3.8.10
# protoc version >= 3.13.0
# grpc version >= 1.38.0

set -e

INPUT_DIR=./proto
OUTPUT_DIR=./mir/protos
rm -rf $OUTPUT_DIR
mkdir -p $OUTPUT_DIR

# gen protobuf py
python -m grpc_tools.protoc \
      -I "$INPUT_DIR" \
      --python_out="$OUTPUT_DIR" \
      "$INPUT_DIR/mir_command.proto"

# gen protobuf pyi for mypy
protoc --plugin=protoc-gen-mypy=$(which protoc-gen-mypy) --mypy_out=$OUTPUT_DIR "$INPUT_DIR/mir_command.proto" \
&& mv $OUTPUT_DIR/proto/mir_command_pb2.pyi $OUTPUT_DIR/ \
&& rm -rf $OUTPUT_DIR/proto

touch $OUTPUT_DIR/__init__.py
