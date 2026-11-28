"""Authenticated provider registration API."""

import sqlite3

from fastapi import APIRouter, HTTPException, Request, Response

from backend.api.auth import COOKIE_NAME, require_same_origin
from backend.auth.sessions import get_session_email
from backend.registration.profiles import get_profile, save_profile
from backend.registration.matching import find_existing_provider

router = APIRouter(prefix="/api/registration")


def require_verified_email(request):
    email = get_session_email(
        request.cookies.get(COOKIE_NAME)
    )

    if not email:
        raise HTTPException(
            status_code=401,
            detail="Please sign in first.",
        )

    return email


@router.get("/profile")
def read_profile(request: Request, response: Response):
    response.headers["Cache-Control"] = "no-store"
    email = require_verified_email(request)

    profile = get_profile(email)

    return {
        "account_email": email,
        "profile": profile,
        "prefill": (
            find_existing_provider(email)
            if profile is None else None
        ),
    }


@router.patch("/profile")
def update_profile(
    values: dict,
    request: Request,
    response: Response,
):
    response.headers["Cache-Control"] = "no-store"

    require_same_origin(request)
    email = require_verified_email(request)

    existing = get_profile(email)

    if existing and existing["status"] == "deleted":
        raise HTTPException(
            status_code=409,
            detail="This registration has been deleted.",
        )

    for value in values.values():
        if value is not None and not isinstance(
            value, (str, int, float, bool)
        ):
            raise HTTPException(
                status_code=422,
                detail="Invalid profile field value.",
            )

    try:
        profile = save_profile(email, values)
    except (ValueError, sqlite3.IntegrityError, OverflowError):
        raise HTTPException(
            status_code=422,
            detail="Invalid profile information.",
        )

    return {
        "account_email": email,
        "profile": profile,
    }


@router.put("/photo")
async def upload_photo(request: Request, response: Response):
    from starlette.concurrency import run_in_threadpool
    from backend.registration.photos import (
        MAX_UPLOAD_BYTES,
        process_photo,
    )
    from backend.registration.photo_storage import save_photo

    response.headers["Cache-Control"] = "no-store"
    require_same_origin(request)
    email = require_verified_email(request)

    data = bytearray()

    async for chunk in request.stream():
        if len(data) + len(chunk) > MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=413,
                detail="Maximum photo size is 5 MB.",
            )
        data.extend(chunk)

    try:
        photo = await run_in_threadpool(
            process_photo, bytes(data)
        )
        await run_in_threadpool(save_photo, email, photo)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    return {"profile_photo": photo}


@router.delete("/photo")
def remove_photo(request: Request, response: Response):
    from backend.registration.photo_storage import save_photo

    response.headers["Cache-Control"] = "no-store"
    require_same_origin(request)
    email = require_verified_email(request)

    try:
        save_photo(email, None)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    return {"profile_photo": None}
