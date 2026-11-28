"""Passwordless authentication API."""

import os
import re

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, Field

from backend.auth.rate_limits import RateLimitExceeded
from backend.auth.verification_email import send_verification_email
from backend.auth.verification_tokens import consume_token
from backend.auth.sessions import (
    create_session,
    get_session_email,
    revoke_session,
    SESSION_LIFETIME_SECONDS,
)


router = APIRouter(prefix="/api/auth")

COOKIE_NAME = "sv_session"

EMAIL_PATTERN = re.compile(
    r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
)

TOKEN_PATTERN = re.compile(
    r"^[A-Za-z0-9_-]{43}$"
)


class EmailRequest(BaseModel):
    email: str = Field(min_length=3, max_length=254)


class VerificationRequest(BaseModel):
    token: str = Field(min_length=43, max_length=43)


def require_same_origin(request):
    origin = os.environ.get("AUTH_BASE_URL", "").rstrip("/")

    if not origin:
        raise HTTPException(
            status_code=503,
            detail="Authentication is not configured."
        )

    if request.headers.get("origin") != origin:
        raise HTTPException(
            status_code=403,
            detail="Request origin not allowed."
        )

    return origin


@router.post("/request")
def request_verification(
    payload: EmailRequest,
    request: Request,
    response: Response,
):
    response.headers["Cache-Control"] = "no-store"

    origin = require_same_origin(request)
    email = payload.email.strip().lower()

    if not EMAIL_PATTERN.fullmatch(email):
        raise HTTPException(
            status_code=422,
            detail="Enter a valid email address."
        )

    if os.environ.get("AUTH_EMAIL_ENABLED") != "1":
        raise HTTPException(
            status_code=503,
            detail="Email verification is currently disabled."
        )

    try:
        send_verification_email(
            email,
            origin,
            client_ip=request.client.host if request.client else None,
        )

    except RateLimitExceeded:
        raise HTTPException(
            status_code=429,
            detail="Please wait before requesting another link."
        )

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Unable to send verification email."
        )

    return {
        "message": "Check your email for a secure sign-in link."
    }


@router.post("/verify")
def verify_email(
    payload: VerificationRequest,
    request: Request,
    response: Response,
):
    response.headers["Cache-Control"] = "no-store"
    require_same_origin(request)

    if not TOKEN_PATTERN.fullmatch(payload.token):
        raise HTTPException(
            status_code=400,
            detail="Invalid verification link."
        )

    email = consume_token(payload.token)

    if email is None:
        raise HTTPException(
            status_code=400,
            detail="Verification link is invalid or expired."
        )

    previous_token = request.cookies.get(COOKIE_NAME)
    session_token = create_session(email)

    if previous_token:
        revoke_session(previous_token)

    response.set_cookie(
        key=COOKIE_NAME,
        value=session_token,
        max_age=SESSION_LIFETIME_SECONDS,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
    )

    return {
        "authenticated": True,
        "email": email,
    }


@router.get("/session")
def session_status(
    request: Request,
    response: Response,
):
    response.headers["Cache-Control"] = "no-store"

    token = request.cookies.get(COOKIE_NAME)
    email = get_session_email(token)

    return {
        "authenticated": email is not None,
        "email": email,
    }


@router.post("/logout")
def logout(
    request: Request,
    response: Response,
):
    response.headers["Cache-Control"] = "no-store"
    require_same_origin(request)

    token = request.cookies.get(COOKIE_NAME)

    if token:
        revoke_session(token)

    response.delete_cookie(
        key=COOKIE_NAME,
        path="/",
        httponly=True,
        secure=True,
        samesite="lax",
    )

    return {"authenticated": False}
