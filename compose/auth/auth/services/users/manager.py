from __future__ import annotations

import logging
import uuid
from collections.abc import Sequence
from typing import Any, Annotated

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordRequestForm

from .db import (
    AbstractUserDatabase,
    UserDatabaseDep,
)
from .exceptions import (
    UserDoesNotExist,
    UserAlreadyExists,
)
from .login_history import (
    LoginHistoryCreate,
    AbstractLoginHistoryService,
    LoginHistoryServiceDep,
    LoginHistoryServiceException,
)
from .models import (
    UserCreate,
    UserUpdate,
)
from .password import (
    AbstractPasswordHelper,
    PasswordHelperDep,
)
from ..pagination import (
    PageParams,
)
from ...models.sqlalchemy import User

logger = logging.getLogger(__name__)


class UserManager:
    user_db: AbstractUserDatabase
    password_helper: AbstractPasswordHelper
    login_history_service: AbstractLoginHistoryService

    def __init__(
            self,
            *,
            user_db: AbstractUserDatabase,
            password_helper: AbstractPasswordHelper,
            login_history_service: AbstractLoginHistoryService) -> None:
        self.user_db = user_db
        self.password_helper = password_helper
        self.login_history_service = login_history_service

    async def get(self, *, user_id: uuid.UUID) -> User:
        user = await self.user_db.get(user_id=user_id)

        if user is None:
            raise UserDoesNotExist

        return user

    async def get_by_login(self, *, login: str) -> User:
        user = await self.user_db.get_by_login(login=login)

        if user is None:
            raise UserDoesNotExist

        return user

    async def get_by_email(self, *, email: str) -> User:
        user = await self.user_db.get_by_email(email=email)

        if user is None:
            raise UserDoesNotExist

        return user

    async def get_list(self, *, page_params: PageParams) -> Sequence[User]:
        return await self.user_db.get_list(page_params=page_params)

    async def create(self, *, user_create: UserCreate) -> User:
        existing_user = await self.user_db.get_by_login(login=user_create.login)

        if existing_user is not None:
            raise UserAlreadyExists

        user_create_dict = user_create.model_dump()
        password = user_create_dict.pop('password')
        user_create_dict['password'] = self.password_helper.hash(password=password)

        created_user = await self.user_db.create(create_dict=user_create_dict)

        return created_user

    async def update(self, *, user: User, user_update: UserUpdate) -> User:
        update_dict = user_update.model_dump(exclude_unset=True)

        for field, value in update_dict.items():
            if field == 'login' and value != user.login:
                try:
                    await self.get_by_login(login=value)
                    raise UserAlreadyExists

                except UserDoesNotExist:
                    update_dict['login'] = value

            elif field == 'password' and value is not None:
                update_dict['password'] = self.password_helper.hash(password=value)

            else:
                update_dict[field] = value

        updated_user = await self.user_db.update(user=user, update_dict=update_dict)

        if updated_user is None:
            raise UserDoesNotExist

        return updated_user

    async def authenticate(self, *, credentials: OAuth2PasswordRequestForm, request: Request) -> User | None:
        try:
            user = await self.get_by_login(login=credentials.username)

        except UserDoesNotExist:
            # Вычисляем хеш пароля, чтобы исключить возможность атаки по времени
            # https://code.djangoproject.com/ticket/20760
            self.password_helper.hash(password=credentials.password)
            return None

        if user.password is None:
            return None

        verified, updated_password_hash = self.password_helper.verify_and_update(
            password=credentials.password,
            password_hash=user.password,
        )

        if not verified:
            return None

        # Обновляем хеш пароля, если был использован более надежный алгоритм
        if updated_password_hash is not None:
            await self.user_db.update(user=user, update_dict={
                'password': updated_password_hash,
            })

        await self._log_user_login(request=request, user=user)

        return user

    async def _log_user_login(self, *, request: Request, user: User) -> None:
        login_history_create = LoginHistoryCreate(
            user_agent=request.headers.get('User-Agent') or '',
        )

        try:
            await self.login_history_service.create(
                user_id=user.id,
                login_history_create=login_history_create,
            )

        except LoginHistoryServiceException as e:
            logger.exception(e)

    async def get_by_oauth_account(self, *, oauth_name: str, account_id: str) -> User:
        user = await self.user_db.get_by_oauth_account(
            oauth_name=oauth_name,
            account_id=account_id,
        )

        if user is None:
            raise UserDoesNotExist

        return user

    async def oauth_callback(self,
                             *,
                             oauth_name: str,
                             access_token: str,
                             account_id: str,
                             account_email: str,
                             expires_at: int | None = None,
                             refresh_token: str | None = None) -> User:
        account_email = account_email.lower()
        oauth_account_dict: dict[str, Any] = {
            'oauth_name': oauth_name,
            'access_token': access_token,
            'account_id': account_id,
            'account_email': account_email,
            'expires_at': expires_at,
            'refresh_token': refresh_token,
        }

        try:
            user = await self.get_by_oauth_account(oauth_name=oauth_name, account_id=account_id)

        except UserDoesNotExist:
            try:
                user = await self.get_by_email(email=account_email)

            except UserDoesNotExist:
                password = self.password_helper.generate()
                user = await self.user_db.create(create_dict={
                    'email': account_email,
                    'password': self.password_helper.hash(password=password),
                })

            user = await self.user_db.add_oauth_account(user=user, create_dict=oauth_account_dict)

            return user

        for oauth_account in await user.awaitable_attrs.oauth_accounts:
            if all([
                oauth_account.oauth_name == oauth_name,
                oauth_account.account_id == account_id,
            ]):
                user = await self.user_db.update_oauth_account(
                    user=user,
                    oauth_account=oauth_account,
                    update_dict=oauth_account_dict,
                )
                break

        return user


async def get_user_manager(user_db: UserDatabaseDep,
                           password_helper: PasswordHelperDep,
                           login_history_service: LoginHistoryServiceDep) -> UserManager:
    return UserManager(
        user_db=user_db,
        password_helper=password_helper,
        login_history_service=login_history_service,
    )


UserManagerDep = Annotated[UserManager, Depends(get_user_manager)]
