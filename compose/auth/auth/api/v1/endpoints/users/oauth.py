from __future__ import annotations

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    Request,
    Response,
    status,
)

from .....services.users import (
    UserServiceDep,
    OAuth2AuthorizeResponse,
    OAuthInvalidProvider,
    OAuthInvalidStateToken,
    OAuthEmailNotAvailable,
)

router = APIRouter()


@router.get(
    '/{provider_name}/authorize',
    name='oauth:authorize',
    response_model=OAuth2AuthorizeResponse,
)
async def authorize(*,
                    request: Request,
                    provider_name: str,
                    scope: list[str] | None = Query(None),
                    user_service: UserServiceDep) -> OAuth2AuthorizeResponse:
    try:
        return await user_service.oauth_authorize(
            request=request,
            provider_name=provider_name,
            scope=scope,
        )

    except OAuthInvalidProvider:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


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
                   user_service: UserServiceDep) -> Response:
    try:
        return await user_service.oauth_callback(
            request=request,
            provider_name=provider_name,
            code=code,
            code_verifier=code_verifier,
            state=state,
            error=error,
        )

    except OAuthInvalidProvider:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    except OAuthInvalidStateToken as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except OAuthEmailNotAvailable as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
