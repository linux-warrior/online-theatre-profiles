from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Request, status
from pydantic import BaseModel

from .common import (
    ErrorCode,
)
from .....services.users import (
    OAuthServiceDep,
    InvalidOAuthProvider,
    InvalidStateToken,
    AuthenticationBackendDep,
    UserManagerDep,
    UserAlreadyExists,
)

router = APIRouter()


class OAuth2AuthorizeResponse(BaseModel):
    authorization_url: str


@router.get(
    '/{provider_name}/authorize',
    name='oauth:authorize',
    response_model=OAuth2AuthorizeResponse,
)
async def authorize(*,
                    request: Request,
                    provider_name: str,
                    scope: list[str] | None = Query(None),
                    oauth_service: OAuthServiceDep) -> OAuth2AuthorizeResponse:
    try:
        authorization_url = await oauth_service.get_authorization_url(
            request=request,
            provider_name=provider_name,
            scope=scope,
        )

    except InvalidOAuthProvider:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return OAuth2AuthorizeResponse(authorization_url=authorization_url)


@router.get(
    '/{provider_name}/callback',
    name='oauth:callback',
)
async def callback(*,
                   request: Request,
                   provider_name: str,
                   code: str | None = Query(None),
                   code_verifier: str | None = Query(None),
                   state: str | None = Query(None),
                   error: str | None = Query(None),
                   oauth_service: OAuthServiceDep,
                   user_manager: UserManagerDep,
                   backend: AuthenticationBackendDep):
    try:
        oauth_result = await oauth_service.authorize(
            request=request,
            provider_name=provider_name,
            code=code,
            code_verifier=code_verifier,
            state=state,
            error=error,
        )

    except InvalidOAuthProvider:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    except InvalidStateToken:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.OAUTH_INVALID_STATE_TOKEN,
        )

    if oauth_result.user_email is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.OAUTH_EMAIL_NOT_AVAILABLE,
        )

    try:
        user = await user_manager.oauth_callback(
            oauth_name=oauth_result.client_name,
            access_token=oauth_result.token['access_token'],
            account_id=oauth_result.user_id,
            account_email=oauth_result.user_email,
            expires_at=oauth_result.token.get('expires_at'),
            refresh_token=oauth_result.token.get('refresh_token'),
        )

    except UserAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.OAUTH_USER_ALREADY_EXISTS,
        )

    return await backend.login(user)
