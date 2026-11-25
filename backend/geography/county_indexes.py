"""Build lookup indexes for official county records."""

from collections import defaultdict


def build_county_indexes(records):
    """Index counties by official GEOID and state code."""

    by_geoid = {}
    by_state = defaultdict(list)

    for record in records:
        geoid = record["geoid"]
        state = record["state_code"]

        if geoid in by_geoid:
            raise ValueError(f"Duplicate county GEOID: {geoid}")

        by_geoid[geoid] = record
        by_state[state].append(record)

    for counties in by_state.values():
        counties.sort(key=lambda record: record["county_name"].casefold())

    return {
        "by_geoid": by_geoid,
        "by_state": dict(by_state),
    }
