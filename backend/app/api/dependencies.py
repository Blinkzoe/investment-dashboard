import secrets
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings
from app.core.security import decode_access_token


bearer_scheme = HTTPBearer(auto_error=False)


def require_import_token(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
) -> None:
    expected_token = settings.import_api_token

    if not expected_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Import API authentication is not configured",
        )

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not secrets.compare_digest(credentials.credentials, expected_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid import API token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_auth(investment_session: Annotated[str | None, Cookie()] = None) -> str:
    username = decode_access_token(investment_session) if investment_session else None
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required", headers={"WWW-Authenticate": "Bearer"})
    return username
