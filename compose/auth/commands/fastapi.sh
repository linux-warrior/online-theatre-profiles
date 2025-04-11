#!/usr/bin/env bash

set -e

app_path=/opt/app/auth/main.py

fastapi_dev() {
    fastapi dev --host 0.0.0.0 "$app_path"
}

fastapi_run() {
    fastapi_args=()

    if [[ "$FASTAPI_WORKERS" ]]; then
        fastapi_args+=(--workers "$FASTAPI_WORKERS")
    fi

    fastapi run "${fastapi_args[@]}" "$app_path"
}

main() {
    local command="$1"

    case "$command" in
        dev) fastapi_dev; exit ;;
        run) fastapi_run; exit ;;
    esac

    fastapi_run
}

main "$@"
