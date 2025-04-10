#!/usr/bin/env bash

set -e

BASE_DIR=/opt/app
SOURCE_PATHS=("$BASE_DIR/tests")

main() {
    mypy "${SOURCE_PATHS[@]}"
}

main "$@"
