#!/usr/bin/env bash

set -e

python manage.py migrate --noinput

export DJANGO_SUPERUSER_PASSWORD="$SUPERUSER_PASSWORD"

python manage.py createsuperuser --noinput --username="$SUPERUSER_LOGIN" --email '' || :
