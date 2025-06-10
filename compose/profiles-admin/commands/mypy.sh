#!/usr/bin/env bash

set -e

BASE_DIR=/opt/app
SOURCE_PATHS=("$BASE_DIR/config" "$BASE_DIR/manage.py")

main() {
    mypy "${SOURCE_PATHS[@]}"
}

main "$@"
