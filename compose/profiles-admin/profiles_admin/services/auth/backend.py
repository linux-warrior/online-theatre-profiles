from __future__ import annotations

import logging
from typing import Any

import httpx
from asgiref.sync import sync_to_async
from django.contrib.auth.backends import (
    ModelBackend,
)
from django.contrib.auth.models import User

from .service import AuthService

logger = logging.getLogger(__name__)


class AuthServiceUserBackend(ModelBackend):
    def authenticate(self,
                     request: Any,
                     username: str | None = None,
                     password: str | None = None,
                     **kwargs: Any) -> User | None:
        if username is None or password is None:
            return None

        auth_service = AuthService(
            user_login=username,
            user_password=password,
        )

        try:
            current_user = auth_service.get_user_profile()
        except httpx.HTTPError as e:
            logger.exception(e)
            return None

        if not current_user.login:
            return None

        user, _created = User.objects.update_or_create(
            username=current_user.login,
            defaults={
                'email': current_user.email or '',
                'is_staff': current_user.is_admin,
                'is_superuser': current_user.is_superuser,
            }
        )

        return user

    async def aauthenticate(self,
                            request: Any,
                            username: str | None = None,
                            password: str | None = None,
                            **kwargs: Any) -> User | None:
        return await sync_to_async(self.authenticate)(
            request,
            username=username,
            password=password,
            **kwargs,
        )
