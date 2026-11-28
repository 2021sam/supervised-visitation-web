"""Authenticated provider registration API."""

import sqlite3

from fastapi import APIRouter, HTTPException, Request, Response

from backend.api.auth import COOKIE_NAME, require_same_origin
from backend.auth.sessions import get_session_email
from backend.registration.profiles import get_profile, save_profile
from backend.registration.matching import find_existing_provider
from backend.registration.updates import update_registration

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
        profile, published = update_registration(
            email, lambda: save_profile(email, values)
        )
    except (ValueError, sqlite3.IntegrityError, OverflowError):
        raise HTTPException(
            status_code=422,
            detail="Invalid profile information.",
        )

    return {
        "account_email": email,
        "profile": profile,
        "publication_success": published,
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
        _, published = await run_in_threadpool(
            update_registration,
            email,
            lambda: save_photo(email, photo),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    return {
        "profile_photo": photo,
        "publication_success": published,
    }


@router.delete("/photo")
def remove_photo(request: Request, response: Response):
    from backend.registration.photo_storage import save_photo

    response.headers["Cache-Control"] = "no-store"
    require_same_origin(request)
    email = require_verified_email(request)

    try:
        _, published = update_registration(
            email, lambda: save_photo(email, None)
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    return {
        "profile_photo": None,
        "publication_success": published,
    }


@router.post("/profile/action")
def profile_action(
    values: dict,
    request: Request,
    response: Response,
):
    import logging
    import os

    from backend.registration.publication import publish_action

    response.headers["Cache-Control"] = "no-store"

    require_same_origin(request)
    email = require_verified_email(request)

    if os.environ.get("PROFILE_PUBLICATION_ENABLED") != "1":
        raise HTTPException(
            status_code=503,
            detail="Profile publication is not yet enabled.",
        )

    action = values.get("action")

    if action not in ("publish", "hide", "delete"):
        raise HTTPException(
            status_code=422,
            detail="Invalid profile action.",
        )

    try:
        profile = publish_action(email, action)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logging.getLogger(__name__).exception(
            "Profile publication failed"
        )
        raise HTTPException(
            status_code=503,
            detail="Unable to update the directory. Please try again.",
        ) from exc

    return {
        "account_email": email,
        "profile": profile,
    }
