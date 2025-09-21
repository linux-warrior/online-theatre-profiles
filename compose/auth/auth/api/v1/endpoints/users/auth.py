from __future__ import annotations

from typing import Annotated

from fastapi import (
    APIRouter,
    Request,
    Response,
    Form,
    Depends,
    HTTPException,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_limiter.depends import RateLimiter

from .....core.config import settings
from .....services.users import (
    UserServiceDep,
    CurrentUserDep,
    TokenDep,
    BadCredentials,
    InvalidToken,
)

router = APIRouter()


@router.post(
    '/login',
    name='auth:login',
    dependencies=[
        Depends(RateLimiter(
            times=settings.ratelimiter.times,
            seconds=settings.ratelimiter.seconds,
        )),
    ],
)
async def login(*,
                request: Request,
                credentials: OAuth2PasswordRequestForm = Depends(),
                user_service: UserServiceDep) -> Response:
    try:
        return await user_service.login(request=request, credentials=credentials)

    except BadCredentials as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    '/logout',
    name='auth:logout',
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            'description': 'Token is invalid or missing.',
        },
    },
)
async def logout(user: CurrentUserDep,
                 token: TokenDep,
                 user_service: UserServiceDep) -> Response:
    return await user_service.logout(user=user, token=token)


@router.post(
    '/refresh',
    name='auth:refresh',
)
async def refresh(refresh_token: Annotated[str, Form()],
                  user_service: UserServiceDep) -> Response:
    try:
        return await user_service.refresh(refresh_token=refresh_token)

    except InvalidToken as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
