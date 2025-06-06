from __future__ import annotations

from ..common import (
    BaseServiceException,
)


class ReviewServiceException(BaseServiceException):
    def get_default_message(self) -> str:
        return 'Review service exception'


class ReviewNotFound(ReviewServiceException):
    def get_default_message(self) -> str:
        return 'Review not found'


class ReviewCreateError(ReviewServiceException):
    def get_default_message(self) -> str:
        return 'Review create error'


class ReviewUpdateError(ReviewServiceException):
    def get_default_message(self) -> str:
        return 'Review update error'
