# syntax=docker/dockerfile:1

FROM bitnami/nginx:1.27.4-debian-12-r9 AS base

FROM base AS dev

USER root

RUN useradd -u 1001 -g root user
COPY --chown=1001:root ./conf/ /opt/bitnami/nginx/conf/

USER 1001

FROM base

COPY ./conf/ /opt/bitnami/nginx/conf/
