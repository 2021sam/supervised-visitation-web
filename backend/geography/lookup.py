"""Retrieve geographic information from supplied indexes."""


def get_zip_records(indexes, zip_code):
    """Return all records associated with a ZIP code."""
    return list(indexes["by_zip"].get(zip_code.strip(), []))


def get_state_cities(indexes, state_code):
    """Return unique postal place names within a state."""
    state = state_code.strip().upper()
    cities = {}

    for record in indexes["by_state"].get(state, []):
        city = record["city"].strip()

        if city:
            cities.setdefault(city.casefold(), city)

    return sorted(cities.values(), key=str.casefold)


def get_city_zip_codes(indexes, state_code, city):
    """Return unique ZIP codes associated with a city."""
    key = (state_code.strip().upper(), city.strip().casefold())

    return sorted({
        record["zip_code"]
        for record in indexes["by_city"].get(key, [])
    })


def get_state_counties(county_indexes, state_code):
    """Return official counties within a state."""
    state = state_code.strip().upper()
    return list(county_indexes["by_state"].get(state, []))


def get_county(county_indexes, geoid):
    """Return an official county record by GEOID."""
    return county_indexes["by_geoid"].get(geoid.strip())
