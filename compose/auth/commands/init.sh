#!/usr/bin/env bash

set -e

alembic upgrade head

typer /opt/app/auth/commands/create_superuser.py run \
    --login="$SUPERUSER_LOGIN" \
    --password="$SUPERUSER_PASSWORD" \
    || :
