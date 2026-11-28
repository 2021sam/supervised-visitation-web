"""Read and save standard travel rates."""

RATE_UNITS = {
    "price_per_mile": "mile",
    "driving_hourly_rate": "hour",
}


def read_travel_rates(db, registration_id):
    values = dict.fromkeys(RATE_UNITS)

    rows = db.execute("""
        SELECT rate_type, amount
        FROM registration_rates
        WHERE registration_id = ?
          AND rate_type IN ('price_per_mile', 'driving_hourly_rate')
          AND minimum_children IS NULL
          AND maximum_children IS NULL
    """, (registration_id,))

    for row in rows:
        values[row["rate_type"]] = row["amount"]

    return values


def save_travel_rates(db, registration_id, values):
    for field, amount in values.items():
        if field not in RATE_UNITS:
            raise ValueError("Unsupported travel rate.")

        if amount is not None and (
            type(amount) is not int
            or amount < 0
            or amount > 9223372036854775807
        ):
            raise ValueError("Invalid travel rate.")

        db.execute("""
            DELETE FROM registration_rates
            WHERE registration_id = ?
              AND rate_type = ?
              AND minimum_children IS NULL
              AND maximum_children IS NULL
        """, (registration_id, field))

        if amount is not None:
            db.execute("""
                INSERT INTO registration_rates (
                    registration_id,
                    rate_type,
                    amount,
                    billing_unit
                )
                VALUES (?, ?, ?, ?)
            """, (
                registration_id,
                field,
                amount,
                RATE_UNITS[field],
            ))
