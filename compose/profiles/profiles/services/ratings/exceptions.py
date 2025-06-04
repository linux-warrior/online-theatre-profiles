from __future__ import annotations

from ..base import (
    BaseServiceException,
)


class RatingServiceException(BaseServiceException):
    def get_default_message(self) -> str:
        return 'Rating service exception'


class RatingNotFound(RatingServiceException):
    def get_default_message(self) -> str:
        return 'Rating not found'


class RatingCreateError(RatingServiceException):
    def get_default_message(self) -> str:
        return 'Rating create error'


class RatingUpdateError(RatingServiceException):
    def get_default_message(self) -> str:
        return 'Rating update error'
