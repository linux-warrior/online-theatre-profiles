from __future__ import annotations

from typing import Annotated

import httpx
from fastapi import HTTPException, Depends, status

from .client import CurrentUserClientDep
from .models import CurrentUser


async def get_current_user(current_user_client: CurrentUserClientDep) -> CurrentUser:
    try:
        user_data = await current_user_client.get_user_profile()

    except httpx.HTTPStatusError as e:
        if e.response.status_code == status.HTTP_403_FORBIDDEN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    except httpx.HTTPError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

    return CurrentUser(**user_data)


CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]
