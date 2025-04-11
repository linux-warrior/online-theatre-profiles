#!/usr/bin/env bash

set -e

alembic upgrade head

export PYTHONPATH=/opt/app:$PYTHONPATH

cli_script_path=/opt/app/scripts/cli.py

python "$cli_script_path" "$SUPERUSER_LOGIN" "$SUPERUSER_PASSWORD"
