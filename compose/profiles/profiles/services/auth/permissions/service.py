from __future__ import annotations

import abc
from typing import Annotated

from fastapi import Depends

from .checkers import (
    AbstractPermissionChecker,
    PermissionChecker,
)
from ..current import (
    CurrentUser,
    CurrentUserDep,
)


class AbstractPermissionService(abc.ABC):
    @abc.abstractmethod
    def get_permission_checker(self) -> AbstractPermissionChecker: ...


class PermissionService(AbstractPermissionService):
    current_user: CurrentUser

    def __init__(self, *, current_user: CurrentUser) -> None:
        self.current_user = current_user

    def get_permission_checker(self) -> AbstractPermissionChecker:
        return PermissionChecker(current_user=self.current_user)


async def get_permission_service(current_user: CurrentUserDep) -> AbstractPermissionService:
    return PermissionService(current_user=current_user)


PermissionServiceDep = Annotated[PermissionService, Depends(get_permission_service)]
