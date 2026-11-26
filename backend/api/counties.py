"""Nationwide county selection API."""

from fastapi import APIRouter
from backend.geography.county_loader import load_counties
from backend.geography.county_indexes import build_county_indexes
from backend.geography.lookup import get_state_counties

router = APIRouter(prefix="/api/counties")

COUNTY_INDEXES = build_county_indexes(load_counties())


@router.get("")
def get_counties(state_code: str):
    counties = get_state_counties(
        COUNTY_INDEXES,
        state_code,
    )

    return {
        "count": len(counties),
        "counties": counties,
    }
