from __future__ import annotations

import logging.config
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager

import redis.asyncio as redis
import sentry_sdk
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi_limiter import FastAPILimiter
from opentelemetry import trace
from opentelemetry.baggage.propagation import W3CBaggagePropagator
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.composite import CompositePropagator
from opentelemetry.propagators.jaeger import JaegerPropagator
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

from .api.v1.endpoints import (
    roles,
    permissions
)
from .api.v1.endpoints.users import (
    auth,
    oauth,
    register,
    users,
)
from .core import settings, LOGGING

logging.config.dictConfig(LOGGING)

if settings.sentry.enable_sdk:
    sentry_sdk.init(
        dsn=settings.sentry.dsn,
        traces_sample_rate=settings.sentry.traces_sample_rate,
        profiles_sample_rate=settings.sentry.profiles_sample_rate,
        enable_tracing=settings.sentry.enable_tracing,
    )
    sentry_sdk.set_tag("service_name", "auth-service")


def configure_otel() -> None:
    if not settings.otel.enabled:
        return

    resource = Resource(attributes={
        SERVICE_NAME: settings.otel.service_name,
    })
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    span_exporter = OTLPSpanExporter(endpoint=settings.otel.exporter_otlp_http_endpoint)
    span_processor = BatchSpanProcessor(span_exporter)
    tracer_provider.add_span_processor(span_processor)

    set_global_textmap(CompositePropagator([
        TraceContextTextMapPropagator(),
        W3CBaggagePropagator(),
        JaegerPropagator(),
    ]))


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[dict]:
    configure_otel()

    async with (
        redis.Redis(host=settings.redis.host, port=settings.redis.port) as redis_client,
    ):
        await FastAPILimiter.init(redis_client)
        yield {
            'redis_client': redis_client,
        }


base_api_prefix = '/auth/api'
app = FastAPI(
    title='Auth service',
    description='Authentication & authorization service.',
    docs_url=f'{base_api_prefix}/openapi',
    openapi_url=f'{base_api_prefix}/openapi.json',
    lifespan=lifespan,
)
FastAPIInstrumentor.instrument_app(
    app,
    excluded_urls=f'{base_api_prefix}/_health',
    http_capture_headers_server_request=['X-Request-Id'],
)


@app.middleware('http')
async def check_request_id(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    if settings.otel.enabled and settings.otel.request_id_required:
        request_id = request.headers.get('X-Request-Id')

        if not request_id:
            return JSONResponse({
                'detail': 'X-Request-Id is required',
            }, status_code=status.HTTP_400_BAD_REQUEST)

    return await call_next(request)


@app.get(f'{base_api_prefix}/_health')
async def healthcheck():
    return {}


auth_api_prefix = f'{base_api_prefix}/v1'

app.include_router(
    auth.router,
    prefix=f'{auth_api_prefix}/jwt',
    tags=['auth'],
)
app.include_router(
    oauth.router,
    prefix=f'{auth_api_prefix}/oauth',
    tags=['auth'],
)
app.include_router(
    register.router,
    prefix=auth_api_prefix,
    tags=['register'],
)
app.include_router(
    users.router,
    prefix=f'{auth_api_prefix}/users',
    tags=['users'],
)
app.include_router(
    roles.router,
    prefix=f'{auth_api_prefix}/roles',
    tags=['roles']
)
app.include_router(
    permissions.router,
    prefix=f'{auth_api_prefix}/permissions',
    tags=['permissions']
)
