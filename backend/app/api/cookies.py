"""Helper único para las cookies de sesión. Centraliza flags y expiración."""

from fastapi import Response

from app.config import Settings


def establecer_cookie_sesion(
    response: Response, settings: Settings, token: str, max_age: int
) -> None:
    response.set_cookie(
        key=settings.auth_cookie_name,
        value=token,
        max_age=max_age,
        httponly=True,
        samesite="lax",
        secure=settings.auth_cookie_secure,
        path="/api",
    )


def limpiar_cookie_sesion(response: Response, settings: Settings) -> None:
    response.delete_cookie(
        key=settings.auth_cookie_name,
        path="/api",
        samesite="lax",
        secure=settings.auth_cookie_secure,
    )
