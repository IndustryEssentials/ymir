#!/bin/bash
set -e

INPUT_DIR=./
OUTPUT_DIR=./

python -m grpc_tools.protoc \
       -I "$INPUT_DIR" \
       --grpc_python_out=$OUTPUT_DIR \
       --python_out=$OUTPUT_DIR \
       "$INPUT_DIR/backend.proto"

sed -i -r 's/^import (.*_pb2.*)/from proto import \1/g' $OUTPUT_DIR/*_pb2*.py
