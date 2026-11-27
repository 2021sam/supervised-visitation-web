"""Supervisor directory API."""

from fastapi import APIRouter, HTTPException, Query

from backend.database.supervisors import list_supervisors
from backend.api.counties import COUNTY_INDEXES
from backend.geography.county_resolver import resolve_county

from backend.geography.loader import load_zip_records
from backend.geography.indexes import build_indexes
from backend.search.supervisor_radius import search_supervisors_by_radius

ZIP_INDEXES = build_indexes(load_zip_records())

router = APIRouter(prefix="/api/supervisors")


@router.get("")
def get_supervisors(
    state_code: str | None = None,
    county: str | None = None,
    county_geoid: str | None = None,
    zip_code: str | None = None,
    radius_miles: float | None = Query(
        default=None, ge=0, le=1000
    ),
):
    if zip_code is not None or radius_miles is not None:
        if not state_code or not zip_code or radius_miles is None:
            raise HTTPException(
                status_code=400,
                detail="State, ZIP code and radius are required",
            )

        if county or county_geoid is not None:
            raise HTTPException(
                status_code=400,
                detail="Choose county or mileage search, not both",
            )

        supervisors = list_supervisors(state_code=state_code)

        try:
            results = search_supervisors_by_radius(
                supervisors,
                ZIP_INDEXES,
                state_code,
                zip_code,
                radius_miles,
            )
        except ValueError as error:
            raise HTTPException(
                status_code=400,
                detail=str(error),
            ) from error

        return {
            "count": len(results),
            "supervisors": results,
        }

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
