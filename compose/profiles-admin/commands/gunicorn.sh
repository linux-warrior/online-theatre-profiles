#!/usr/bin/env bash

set -e

gunicorn \
    config.wsgi \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-4}" \
