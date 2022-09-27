#!/bin/bash
set -e

# pip/conda(mac) install grpcio==1.38.0
# pip install grpcio_tools==1.38.0

INPUT_DIR=./
OUTPUT_DIR=./

python -m grpc_tools.protoc \
       -I "$INPUT_DIR" \
       -I "../../../../command/proto/" \
       --grpc_python_out=$OUTPUT_DIR \
       --python_out=$OUTPUT_DIR \
       "$INPUT_DIR/backend.proto"

sed -i.bak -r 's/^import (.*_pb2.*)/from mir.protos import \1/g' $OUTPUT_DIR/*_pb2.py && rm *.bak
sed -i.bak -r 's/^import (.*_pb2.*)/from proto import \1/g' $OUTPUT_DIR/*_pb2_grpc.py && rm *.bak
