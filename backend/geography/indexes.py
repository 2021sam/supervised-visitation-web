"""Build geographic lookup indexes from supplied records."""

from collections import defaultdict


def build_indexes(records):
    """Index geographic records without discarding duplicates."""

    by_zip = defaultdict(list)
    by_state = defaultdict(list)
    by_city = defaultdict(list)
    by_county = defaultdict(list)

    for record in records:
        state = record["state_code"]
        city = record["city"].strip().casefold()
        county = record["county_code"]

        by_zip[record["zip_code"]].append(record)

        if state:
            by_state[state].append(record)

            if city:
                by_city[(state, city)].append(record)

            if county:
                by_county[(state, county)].append(record)

    return {
        "by_zip": dict(by_zip),
        "by_state": dict(by_state),
        "by_city": dict(by_city),
        "by_county": dict(by_county),
    }
