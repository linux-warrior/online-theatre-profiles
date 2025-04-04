#!/usr/bin/env bash

set -e

run_server() {
    docker compose up "$@"
}

run_server_dev() {
    docker compose -f compose.dev.yaml up --watch "$@"
}

main() {
    local command="$1"
    local docker_compose_args=(--pull always --build --force-recreate --remove-orphans)

    case "$command" in
        dev) run_server_dev "${docker_compose_args[@]}"; exit ;;
    esac

    run_server "${docker_compose_args[@]}"
}

main "$@"
