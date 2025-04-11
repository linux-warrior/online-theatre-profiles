#!/usr/bin/env bash

set -e

docker_compose() {
    docker compose -f compose.lint.yaml "$@"
}

docker_compose_up() {
    COMPOSE_BAKE=true docker_compose up --remove-orphans "$@"
}

start_services() {
    local docker_compose_args=(-d)

    if [[ "$PULL_POLICY" ]]; then
        docker_compose_args+=(--pull "$PULL_POLICY")
    fi

    if [[ ! "$SKIP_BUILD" ]]; then
        docker_compose_args+=(--build)
    fi

    docker_compose_up "${docker_compose_args[@]}"
}

watch_services() {
    docker_compose_up --watch --pull always --build --force-recreate
}

run_command() {
    declare -A commands
    local commands=(
        [mypy]=/opt/app/commands/mypy.sh
        [ruff]=/opt/app/commands/ruff.sh
    )

    local services=(
        movies
        tests
        auth
        etl
    )

    declare -A services_set
    local services_set=()

    for _service in "${services[@]}"; do
        services_set[$_service]=1
    done

    local command="$1"
    local service="$2"

    local exec_command

    if [[ "$command" ]]; then
        exec_command="${commands[$command]}"
    fi

    if [[ ! "$exec_command" ]]; then
        echo "Invalid command name '$command'."
        exit 1
    fi

    local exec_services=()

    if [[ "$service" ]]; then
        if [[ ! "${services_set[$service]}" ]]; then
            echo "Invalid service name '$service'."
            exit 1
        fi

        exec_services+=("$service")
    else
        exec_services+=("${services[@]}")
    fi

    local exit_codes=()

    for exec_service in "${exec_services[@]}"; do
        local exit_code=0

        echo "Running command '$exec_command' for service '$exec_service'."
        docker_compose exec "$exec_service" "$exec_command" || exit_code=$?

        exit_codes+=("$exit_code")
    done

    for exit_code in "${exit_codes[@]}"; do
        if ((exit_code != 0)); then
            exit "$exit_code"
        fi
    done
}

main() {
    local command="$1"

    if [[ ! "$command" ]]; then
        echo "Command name is required."
        exit 1
    fi

    if [[ "$command" == "watch" ]]; then
        shift 1

        if [[ ! "$1" ]]; then
            watch_services
            exit
        fi
    else
        start_services
    fi

    local command="$1"
    local service="$2"

    run_command "$command" "$service"
}

main "$@"
