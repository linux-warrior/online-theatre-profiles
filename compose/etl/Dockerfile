# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.13

FROM python:${PYTHON_VERSION}-slim AS base

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/app

FROM base AS venv

ENV PATH="/root/.local/bin:$PATH"

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --user pipx==1.7.1
RUN pipx install poetry==2.1.3

ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN python -m venv "$VIRTUAL_ENV"
RUN --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=poetry.lock,target=poetry.lock \
    --mount=type=cache,target=/root/.cache/pypoetry \
    poetry install --no-ansi --no-interaction

FROM venv AS venv-dev

RUN --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=poetry.lock,target=poetry.lock \
    --mount=type=cache,target=/root/.cache/pypoetry \
    poetry install --no-ansi --no-interaction --only dev

FROM base AS common

ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

FROM common AS lint

COPY --from=venv-dev "$VIRTUAL_ENV" "$VIRTUAL_ENV"
COPY ./pyproject.toml .
COPY ./schema/ ./schema/
COPY ./etl/ ./etl/

COPY ./commands/ ./commands/
RUN chmod +x ./commands/*.sh

COPY ./docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

FROM common

COPY --from=venv "$VIRTUAL_ENV" "$VIRTUAL_ENV"
COPY ./pyproject.toml .
COPY ./schema/ ./schema/
COPY ./etl/ ./etl/

COPY ./commands/ ./commands/
RUN chmod +x ./commands/*.sh

COPY ./docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

VOLUME /opt/app/data
VOLUME /opt/app/logs

ENTRYPOINT ["/opt/app/docker-entrypoint.sh"]
CMD ["/opt/app/commands/transfer_data.sh"]
