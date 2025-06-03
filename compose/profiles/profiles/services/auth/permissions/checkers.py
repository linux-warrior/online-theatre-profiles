from __future__ import annotations

import abc
import uuid

from .exceptions import PermissionDenied
from ..current import CurrentUser


class AbstractPermissionChecker(abc.ABC):
    @abc.abstractmethod
    async def check_read_permission(self, *, user_id: uuid.UUID | None = None) -> None: ...

    @abc.abstractmethod
    async def check_create_permission(self, *, user_id: uuid.UUID | None = None) -> None: ...

    @abc.abstractmethod
    async def check_update_permission(self, *, user_id: uuid.UUID | None = None) -> None: ...

    @abc.abstractmethod
    async def check_delete_permission(self, *, user_id: uuid.UUID | None = None) -> None: ...


class PermissionChecker(AbstractPermissionChecker):
    current_user: CurrentUser

    def __init__(self, *, current_user: CurrentUser) -> None:
        self.current_user = current_user

    async def check_read_permission(self, *, user_id: uuid.UUID | None = None) -> None:
        await self._check_current_user(user_id=user_id)

    async def check_create_permission(self, *, user_id: uuid.UUID | None = None) -> None:
        await self._check_current_user(user_id=user_id)

    async def check_update_permission(self, *, user_id: uuid.UUID | None = None) -> None:
        await self._check_current_user(user_id=user_id)

    async def check_delete_permission(self, *, user_id: uuid.UUID | None = None) -> None:
        await self._check_current_user(user_id=user_id)

    async def _check_current_user(self, *, user_id: uuid.UUID | None = None) -> None:
        if user_id is None or self.current_user.id == user_id:
            return

        if self.current_user.is_superuser or 'profiles.admin' in self.current_user.permissions:
            return

        raise PermissionDenied
