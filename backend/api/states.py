"""Nationwide state selection API."""

from fastapi import APIRouter
from backend.geography.loader import load_states

router = APIRouter(prefix="/api/states")

STATES = sorted(
    load_states(),
    key=lambda state: state["state_name"].casefold(),
)


@router.get("")
def get_states():
    return {
        "count": len(STATES),
        "states": STATES,
    }
