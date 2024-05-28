#!/bin/bash

set -xv

cd "$(dirname "$0")"
GOBIN=$HOME/local/bin go install -v ./...
