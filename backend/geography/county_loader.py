"""Load official Census county and county-equivalent records."""

import csv
import math
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data/census/counties.txt"


def load_counties(path=None):
    """Return validated county records from a Census Gazetteer file."""

    path = Path(path) if path else DATA_FILE
    records = []
    seen = set()

    with path.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file, delimiter="|")

        required = {
            "USPS", "GEOID", "NAME", "INTPTLAT", "INTPTLONG"
        }

        if not required.issubset(reader.fieldnames or []):
            raise ValueError("Invalid Census county file columns")

        for row in reader:
            geoid = row["GEOID"].strip()
            state = row["USPS"].strip()
            name = row["NAME"].strip()

            if len(geoid) != 5 or not geoid.isascii() or not geoid.isdigit():
                raise ValueError(f"Invalid county GEOID: {geoid}")

            if geoid in seen:
                raise ValueError(f"Duplicate county GEOID: {geoid}")

            if not state or not name:
                raise ValueError(f"Missing county information: {geoid}")

            latitude = float(row["INTPTLAT"])
            longitude = float(row["INTPTLONG"])

            if not (
                math.isfinite(latitude)
                and math.isfinite(longitude)
                and -90 <= latitude <= 90
                and -180 <= longitude <= 180
            ):
                raise ValueError(f"Invalid coordinates: {geoid}")

            seen.add(geoid)

            records.append({
                "geoid": geoid,
                "state_code": state,
                "state_fips": geoid[:2],
                "county_code": geoid[2:],
                "county_name": name,
                "latitude": latitude,
                "longitude": longitude,
            })

    return records
