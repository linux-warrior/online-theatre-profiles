#!/usr/bin/env bash

set -e

BASE_DIR=/opt/app
SOURCE_PATHS=("$BASE_DIR/movies")

main() {
    mypy "${SOURCE_PATHS[@]}"
}

main "$@"
