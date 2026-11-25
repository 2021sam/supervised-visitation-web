"""Assemble the geographic datasets and indexes."""

from backend.geography.loader import (
    load_states,
    load_zip_records,
)
from backend.geography.indexes import build_indexes
from backend.geography.county_loader import load_counties
from backend.geography.county_indexes import build_county_indexes


def initialize_geography():
    """Load geographic datasets and construct reusable indexes."""

    states = load_states()
    zip_records = load_zip_records()
    counties = load_counties()

    return {
        "states": states,
        "zip_records": zip_records,
        "counties": counties,
        "zip_indexes": build_indexes(zip_records),
        "county_indexes": build_county_indexes(counties),
    }
