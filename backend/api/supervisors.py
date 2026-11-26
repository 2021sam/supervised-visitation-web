"""Supervisor directory API."""

from fastapi import APIRouter, HTTPException

from backend.database.supervisors import list_supervisors
from backend.api.counties import COUNTY_INDEXES
from backend.geography.county_resolver import resolve_county

router = APIRouter(prefix="/api/supervisors")


@router.get("")
def get_supervisors(
    state_code: str | None = None,
    county: str | None = None,
    county_geoid: str | None = None,
):
    if county_geoid is not None:
        resolved = resolve_county(COUNTY_INDEXES, county_geoid)

        if resolved is None:
            raise HTTPException(
                status_code=400,
                detail="Invalid county GEOID",
            )

        if state_code and state_code.strip().upper() != resolved["state_code"]:
            raise HTTPException(
                status_code=400,
                detail="County does not belong to selected state",
            )

        state_code = resolved["state_code"]
        county = resolved["county_name"]

    supervisors = list_supervisors(
        state_code=state_code,
        county=county,
    )

    return {
        "count": len(supervisors),
        "supervisors": supervisors,
    }
