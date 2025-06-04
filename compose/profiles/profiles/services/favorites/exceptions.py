from __future__ import annotations

from ..base import (
    BaseServiceException,
)


class FavoriteServiceException(BaseServiceException):
    def get_default_message(self) -> str:
        return 'Favorite service exception'


class FavoriteNotFound(FavoriteServiceException):
    def get_default_message(self) -> str:
        return 'Favorite not found'


class FavoriteCreateError(FavoriteServiceException):
    def get_default_message(self) -> str:
        return 'Favorite create error'
