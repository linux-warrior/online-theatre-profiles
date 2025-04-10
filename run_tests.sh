#!/usr/bin/env bash

set -e

PYTHON_VERSION=${PYTHON_VERSION:-3.13}

docker_compose() {
    PROJECT_NAME=movies \
    AUTH_SECRET_KEY=secret \
    AUTH_SUPERUSER_LOGIN=admin \
    AUTH_SUPERUSER_PASSWORD=secret \
    AUTH_POSTGRESQL_DATABASE=auth \
    AUTH_POSTGRESQL_USERNAME=auth \
    AUTH_POSTGRESQL_PASSWORD=secret \
    RATELIMITER_TIMES=1000 \
    RATELIMITER_SECONDS=1 \
    docker compose -f compose.tests.yaml "$@"
}

docker_compose_build() {
    local docker_compose_args=()

    if [[ "$PULL_POLICY" && "$PULL_POLICY" != "never" ]]; then
        docker_compose_args+=(--pull)
    fi

    local build_args=(
        "PYTHON_VERSION=$PYTHON_VERSION"
    )

    for build_arg in "${build_args[@]}"; do
        docker_compose_args+=(--build-arg "$build_arg")
    done

    COMPOSE_BAKE=true docker_compose build "${docker_compose_args[@]}"
}

docker_compose_up() {
    docker_compose_build
    docker_compose up --remove-orphans "$@"
}

start_services() {
    local docker_compose_args=(-d)

    if [[ "$PULL_POLICY" ]]; then
        docker_compose_args+=(--pull "$PULL_POLICY")
    fi

    docker_compose_up "${docker_compose_args[@]}"
}

watch_services() {
    docker_compose_up --watch --force-recreate
}

run_tests() {
    docker_compose exec tests /opt/app/commands/pytest.sh
}

main() {
    local command="$1"

    case "$command" in
        watch) watch_services; exit ;;
        tests) run_tests; exit ;;
    esac

    start_services
    run_tests
}

main "$@"
