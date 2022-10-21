#!/bin/bash
set -e

go vet ./...
staticcheck ./...
go test -race -coverprofile=profile.cov -vet=off $(go list ./... | grep -v -e protos -e common/constants -e docs)
go tool cover -func profile.cov && go tool cover -html profile.cov && rm profile.cov
