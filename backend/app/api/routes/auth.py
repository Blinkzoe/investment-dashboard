from typing import Annotated

from fastapi import APIRouter, Cookie, HTTPException, Response, status
from pydantic import BaseModel

from app.core.config import settings
from app.core.security import create_access_token, decode_access_token, verify_password

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

COOKIE_NAME = "investment_session"


class LoginRequest(BaseModel):
    username: str
    password: str


class AuthStatus(BaseModel):
    authenticated: bool
    username: str | None = None


@router.post("/login")
def login(payload: LoginRequest, response: Response) -> AuthStatus:
    if payload.username != settings.auth_username or not verify_password(
        payload.password, settings.auth_password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = create_access_token(payload.username)
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.app_env == "production",
        samesite="lax",
        max_age=60 * 24 * 60 * 60,
        path="/",
    )
    return AuthStatus(authenticated=True, username=payload.username)


@router.post("/logout")
def logout(response: Response) -> dict[str, bool]:
    response.delete_cookie(key=COOKIE_NAME, path="/")
    return {"authenticated": False}


@router.get("/me", response_model=AuthStatus)
def auth_status(
    investment_session: Annotated[str | None, Cookie()] = None,
) -> AuthStatus:
    username = decode_access_token(investment_session) if investment_session else None
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return AuthStatus(authenticated=True, username=username)
