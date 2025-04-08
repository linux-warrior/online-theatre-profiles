#!/usr/bin/env bash

set -e

BASE_DIR=/opt/app
SOURCE_PATHS=("$BASE_DIR/movies")

LINT_DIR=$BASE_DIR/.lint
RUFF_JSON_FILE=$LINT_DIR/ruff.json
RUFF_HTML_DIR=$LINT_DIR/ruff_html

main() {
    rm -rf "$RUFF_JSON_FILE" "$RUFF_HTML_DIR"
    ruff check --output-format json "${SOURCE_PATHS[@]}" >"$RUFF_JSON_FILE" || :

    local ciqar_args=(
        -r "ruff:$RUFF_JSON_FILE"
        -o "$RUFF_HTML_DIR"
    )

    for source_path in "${SOURCE_PATHS[@]}"; do
        ciqar_args+=(-s "$source_path")
    done

    ciqar "${ciqar_args[@]}"
    ruff check "${SOURCE_PATHS[@]}"
}

main "$@"
