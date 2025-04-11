from __future__ import annotations

from typing import Annotated

import httpx
from fastapi import HTTPException, Depends, status

from .client import AuthClientDep
from ...models import User


async def get_auth_user(auth_client: AuthClientDep) -> User:
    try:
        user_data = await auth_client.get_user_profile()

    except httpx.HTTPStatusError as e:
        if e.response.status_code == status.HTTP_403_FORBIDDEN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    except httpx.HTTPError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

    return User(**user_data)


AuthUserDep = Annotated[User, Depends(get_auth_user)]
