from __future__ import annotations

from typing import Annotated

import httpx
from fastapi import Request, Depends


async def get_httpx_client(request: Request) -> httpx.AsyncClient:
    return request.state.httpx_client


HTTPXClientDep = Annotated[httpx.AsyncClient, Depends(get_httpx_client)]
