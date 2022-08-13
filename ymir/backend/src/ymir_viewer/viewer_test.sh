#!/bin/bash
set -e

go test -race -coverprofile=profile.cov -vet=off $(go list ./... | grep -v -e common/protos -e common/constants -e docs)
go tool cover -html profile.cov && rm profile.cov
