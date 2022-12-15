#!/bin/bash
set -e

# pip/conda(mac) install grpcio==1.38.0
# pip install grpcio_tools==1.38.0
# go install google.golang.org/protobuf/cmd/protoc-gen-go@v1.28.1
# go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@v1.2.0

INPUT_DIR="./"
PY_OUTPUT_DIR="./"
GO_OUTPUT_DIR_HEL="../../ymir_hel/"

python -m grpc_tools.protoc \
       -I "$INPUT_DIR" \
       -I "../../../../command/proto/" \
       --grpc_python_out=${PY_OUTPUT_DIR} \
       --python_out=${PY_OUTPUT_DIR} \
       --go_out="${GO_OUTPUT_DIR_HEL}" \
       --go-grpc_out="${GO_OUTPUT_DIR_HEL}" \
       --go-grpc_opt=require_unimplemented_servers=false \
       "${INPUT_DIR}/backend.proto"

sed -i.bak -r 's/^import (.*_pb2.*)/from mir.protos import \1/g' ${PY_OUTPUT_DIR}/*_pb2.py && rm *.bak
sed -i.bak -r 's/^import (.*_pb2.*)/from proto import \1/g' ${PY_OUTPUT_DIR}/*_pb2_grpc.py && rm *.bak
