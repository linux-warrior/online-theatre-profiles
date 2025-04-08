#!/usr/bin/env bash

set -e

gunicorn \
    movies.main:app \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-4}" \
    --worker-class uvicorn_worker.UvicornWorker
