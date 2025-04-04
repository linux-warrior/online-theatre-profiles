from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union

import jwt
from pydantic import SecretStr

SecretType = Union[str, SecretStr]
JWT_ALGORITHM = "HS256"


def _get_secret_value(secret: SecretType) -> str:
    if isinstance(secret, SecretStr):
        return secret.get_secret_value()
    return secret


def generate_jwt(
        data: dict,
        secret: SecretType,
        lifetime_seconds: Optional[int] = None,
        algorithm: str = JWT_ALGORITHM,
) -> str:
    payload = data.copy()
    if lifetime_seconds:
        expire = datetime.now(timezone.utc) + timedelta(seconds=lifetime_seconds)
        payload["exp"] = expire
    return jwt.encode(payload, _get_secret_value(secret), algorithm=algorithm)


def decode_jwt(
        encoded_jwt: str,
        secret: SecretType,
        audience: list[str],
        algorithms: list[str] | None = None,
) -> dict[str, Any]:
    if algorithms is None:
        algorithms = [JWT_ALGORITHM]

    return jwt.decode(
        encoded_jwt,
        _get_secret_value(secret),
        audience=audience,
        algorithms=algorithms,
    )
