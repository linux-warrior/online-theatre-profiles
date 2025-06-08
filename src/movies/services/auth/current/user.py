from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from .models import CurrentUser
from .service import CurrentUserServiceDep


async def get_current_user(current_user_service: CurrentUserServiceDep) -> CurrentUser:
    return await current_user_service.get_user_profile()


CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]
