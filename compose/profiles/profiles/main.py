from __future__ import annotations

from fastapi import FastAPI

base_api_prefix = '/profiles/api'
app = FastAPI(
    title='User profiles service',
    description='A service for user profiles management.',
    docs_url=f'{base_api_prefix}/openapi',
    openapi_url=f'{base_api_prefix}/openapi.json',
)


@app.get(f'{base_api_prefix}/_health')
async def healthcheck():
    return {}
