"""Load and validate nationwide geographic source data."""

import csv
import math
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"


def load_states(path=None):
    """Load state names, codes and flag URLs."""
    path = Path(path) if path else DATA_DIR / "US_States_with_Flags.csv"

    with path.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        required = {"State", "Code", "Flag_URL"}

        if not required.issubset(reader.fieldnames or []):
            raise ValueError(f"Invalid state CSV columns: {path}")

        return [
            {
                "state_name": row["State"].strip(),
                "state_code": row["Code"].strip(),
                "flag_url": row["Flag_URL"].strip(),
            }
            for row in reader
        ]


def load_zip_records(path=None):
    """Load all US geographic records without overwriting duplicates."""
    path = Path(path) if path else DATA_DIR / "US.txt"

    records = []

    with path.open(encoding="utf-8", newline="") as file:
        reader = csv.reader(file, delimiter="\t")

        for line_number, row in enumerate(reader, start=1):

            if len(row) != 12:
                raise ValueError(
                    f"Invalid field count at line {line_number}"
                )

            if row[0] != "US":
                continue

            try:
                latitude = float(row[9])
                longitude = float(row[10])
                accuracy = int(row[11]) if row[11] else None

                if not (
                    math.isfinite(latitude)
                    and math.isfinite(longitude)
                    and -90 <= latitude <= 90
                    and -180 <= longitude <= 180
                ):
                    raise ValueError("Invalid coordinates")

                zip_code = row[1]

                if len(zip_code) != 5 or not zip_code.isascii() or not zip_code.isdigit():
                    raise ValueError("Invalid ZIP code")

            except ValueError as exc:
                raise ValueError(
                    f"Invalid geographic record at line {line_number}: {exc}"
                ) from exc

            records.append({
                "country_code": row[0],
                "zip_code": zip_code,
                "city": row[2],
                "state_name": row[3],
                "state_code": row[4],
                "county_name": row[5],
                "county_code": row[6],
                "admin3_name": row[7],
                "admin3_code": row[8],
                "latitude": latitude,
                "longitude": longitude,
                "accuracy": accuracy,
            })

    return records
