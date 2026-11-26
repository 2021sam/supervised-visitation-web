"""Resolve official county identifiers to directory county names."""

def resolve_county(county_indexes, geoid):
    county = county_indexes["by_geoid"].get(geoid.strip())

    if county is None:
        return None

    name = county["county_name"]
    state_code = county["state_code"]

    # California acquisition records omit the County suffix.
    if state_code == "CA":
        name = name.removesuffix(" County")

    return {
        "geoid": county["geoid"],
        "state_code": state_code,
        "county_name": name,
    }
