from __future__ import annotations

import abc
from typing import Annotated

import httpx
from fastapi import HTTPException, Depends, status

from .client import (
    CurrentUserClient,
    CurrentUserClientDep,
)
from .models import CurrentUser


class AbstractCurrentUserService(abc.ABC):
    @abc.abstractmethod
    async def get_user_profile(self) -> CurrentUser: ...


class CurrentUserService(AbstractCurrentUserService):
    current_user_client: CurrentUserClient

    def __init__(self, *, current_user_client: CurrentUserClient) -> None:
        self.current_user_client = current_user_client

    async def get_user_profile(self) -> CurrentUser:
        return await GetUserProfileRequest(
            current_user_client=self.current_user_client,
        ).send_request()


class CurrentUserServiceRequest[TResponse](abc.ABC):
    current_user_client: CurrentUserClient

    def __init__(self, *, current_user_client: CurrentUserClient) -> None:
        self.current_user_client = current_user_client

    async def send_request(self) -> TResponse:
        try:
            return await self._send_request()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == status.HTTP_403_FORBIDDEN:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
            else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        except httpx.HTTPError:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

    @abc.abstractmethod
    async def _send_request(self) -> TResponse:
        ...


class GetUserProfileRequest(CurrentUserServiceRequest[CurrentUser]):
    async def _send_request(self) -> CurrentUser:
        return await self.current_user_client.get_user_profile()


async def get_current_user_service(current_user_client: CurrentUserClientDep) -> AbstractCurrentUserService:
    return CurrentUserService(current_user_client=current_user_client)


CurrentUserServiceDep = Annotated[CurrentUserService, Depends(get_current_user_service)]
