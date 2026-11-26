"""Supervisor directory API endpoints."""

from fastapi import APIRouter
from backend.database.supervisors import list_supervisors

router = APIRouter(prefix="/api/supervisors")


@router.get("")
def get_supervisors(
    state_code: str | None = None,
    county: str | None = None,
):
    supervisors = list_supervisors(state_code, county)

    return {
        "count": len(supervisors),
        "supervisors": supervisors,
    }
