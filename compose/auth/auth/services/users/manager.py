from __future__ import annotations

import datetime
import uuid
from collections.abc import Sequence
from typing import Any, Optional, Annotated

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import SQLAlchemyError

from . import exceptions
from .authentication.login_history.models import LoginHistoryCreate
from .authentication.login_history.service import LoginHistoryService, LoginHistoryServiceDep
from .db import (
    BaseUserDatabase,
    UserDatabaseDep,
)
from .password import PasswordHelper, PasswordHelperProtocol
from .schemas import UserCreate, UserUpdate
from ...models.sqlalchemy import User


class UserManager:
    """
    User management logic.

    :param user_db: Database adapter instance.
    """

    user_db: BaseUserDatabase
    password_helper: PasswordHelperProtocol
    login_logger: LoginHistoryService

    def __init__(
            self,
            user_db: BaseUserDatabase,
            login_logger: LoginHistoryService,
            password_helper: Optional[PasswordHelperProtocol] = None,
    ):
        self.user_db = user_db
        self.login_logger = login_logger
        if password_helper is None:
            self.password_helper = PasswordHelper()
        else:
            self.password_helper = password_helper

    def parse_id(self, value: Any) -> uuid.UUID:
        if isinstance(value, uuid.UUID):
            return value
        try:
            return uuid.UUID(value)
        except ValueError as e:
            raise exceptions.InvalidID() from e

    async def get(self, id: uuid.UUID) -> User:
        """
        Get a user by id.

        :param id: Id. of the user to retrieve.
        :raises UserDoesNotExist: The user does not exist.
        :return: A user.
        """
        user = await self.user_db.get(id)

        if user is None:
            raise exceptions.UserDoesNotExist

        return user

    async def get_list(self,
                       *,
                       id: uuid.UUID | None = None,
                       created: datetime.datetime | None = None,
                       count: int) -> Sequence[User]:
        return await self.user_db.get_list(
            created=created,
            id=id,
            count=count,
        )

    async def get_by_login(self, user_login: str) -> User:
        """
        Get a user by login.

        :param user_login: Login of the user to retrieve.
        :raises UserDoesNotExist: The user does not exist.
        :return: A user.
        """
        user = await self.user_db.get_by_login(user_login)

        if user is None:
            raise exceptions.UserDoesNotExist

        return user

    async def get_by_email(self, user_email: str) -> User:
        user = await self.user_db.get_by_email(user_email)

        if user is None:
            raise exceptions.UserDoesNotExist

        return user

    async def get_by_oauth_account(self, *, oauth_name: str, account_id: str) -> User:
        user = await self.user_db.get_by_oauth_account(oauth_name=oauth_name, account_id=account_id)

        if user is None:
            raise exceptions.UserDoesNotExist

        return user

    async def create(self, user_create: UserCreate) -> User:
        """
        Create a user in database.

        :param user_create: The UserCreate model to create.
        :raises UserAlreadyExists: A user already exists with the same login.
        :return: A new user.
        """
        existing_user = await self.user_db.get_by_login(user_create.login)
        if existing_user is not None:
            raise exceptions.UserAlreadyExists()

        user_dict = user_create.model_dump()
        password = user_dict.pop("password")
        user_dict["password"] = self.password_helper.hash(password)

        created_user = await self.user_db.create(user_dict)

        return created_user

    async def update(self, user_update: UserUpdate, user: User) -> User:
        """
        Update a user.

        Triggers the on_after_update handler on success

        :param user_update: The UserUpdate model containing
        the changes to apply to the user.
        :param user: The current user to update.
        :return: The updated user.
        """
        updated_user_data = user_update.model_dump(exclude_unset=True)
        updated_user = await self._update(user, updated_user_data)

        return updated_user

    async def authenticate(self, credentials: OAuth2PasswordRequestForm, request: Request) -> User | None:
        """
        Authenticate and return a user following a login and a password.

        Will automatically upgrade password hash if necessary.

        :param request: http request
        :param credentials: The user credentials.
        """
        try:
            user = await self.get_by_login(credentials.username)
        except exceptions.UserDoesNotExist:
            # Run the hasher to mitigate timing attack
            # Inspired from Django: https://code.djangoproject.com/ticket/20760
            self.password_helper.hash(credentials.password)
            return None

        verified, updated_password_hash = self.password_helper.verify_and_update(
            credentials.password, user.password
        )
        if not verified:
            return None

        # Update password hash to a more robust one if needed
        if updated_password_hash is not None:
            await self.user_db.update(user, {"password": updated_password_hash})

        await self._record_user_login(user, request)

        return user

    async def _record_user_login(self, user: User, request: Request) -> None:
        row = LoginHistoryCreate(
            user_id=user.id,
            user_agent=request.headers.get('User-Agent') or '',
        )

        try:
            await self.login_logger.record_to_log(row)
        except SQLAlchemyError:
            pass

    async def _update(self, user: User, update_dict: dict[str, Any]) -> User:
        validated_update_dict = {}

        for field, value in update_dict.items():
            if field == "login" and value != user.login:
                try:
                    await self.get_by_login(value)
                    raise exceptions.UserAlreadyExists()
                except exceptions.UserDoesNotExist:
                    validated_update_dict["login"] = value

            elif field == "password" and value is not None:
                validated_update_dict["password"] = self.password_helper.hash(value)

            else:
                validated_update_dict[field] = value

        return await self.user_db.update(user, validated_update_dict)

    async def oauth_callback(self,
                             *,
                             oauth_name: str,
                             access_token: str,
                             account_id: str,
                             account_email: str,
                             expires_at: int | None = None,
                             refresh_token: str | None = None) -> User:
        account_email = account_email.lower()
        oauth_account_dict = {
            'oauth_name': oauth_name,
            'access_token': access_token,
            'account_id': account_id,
            'account_email': account_email,
            'expires_at': expires_at,
            'refresh_token': refresh_token,
        }

        try:
            user = await self.get_by_oauth_account(oauth_name=oauth_name, account_id=account_id)
        except exceptions.UserDoesNotExist:
            try:
                user = await self.get_by_email(account_email)
            except exceptions.UserDoesNotExist:
                password = self.password_helper.generate()
                user_dict = {
                    'email': account_email,
                    'password': self.password_helper.hash(password),
                }
                user = await self.user_db.create(user_dict)

            user = await self.user_db.add_oauth_account(user, oauth_account_dict)

            return user

        for oauth_account in user.oauth_accounts:
            if all([
                oauth_account.oauth_name == oauth_name,
                oauth_account.account_id == account_id,
            ]):
                user = await self.user_db.update_oauth_account(
                    user,
                    oauth_account,
                    oauth_account_dict,
                )
                break

        return user


async def get_user_manager(user_db: UserDatabaseDep, login_logger: LoginHistoryServiceDep) -> UserManager:
    return UserManager(user_db=user_db, login_logger=login_logger)


UserManagerDep = Annotated[UserManager, Depends(get_user_manager)]
