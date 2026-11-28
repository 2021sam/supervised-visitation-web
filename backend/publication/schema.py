"""Add supported public registration fields to the directory."""

PUBLIC_COLUMNS = {
    "profile_photo": "TEXT",
    "provider_type": "TEXT",
    "professional_title": "TEXT",
    "reference_point": "TEXT",
    "calendar_url": "TEXT",
    "phone_is_cell": "INTEGER",
    "accepting_new_clients": "INTEGER",
    "supervised_visitation": "INTEGER",
    "supervised_exchange": "INTEGER",
    "transportation": "INTEGER",
    "virtual_visitation": "INTEGER",
    "on_site_visitation": "INTEGER",
    "off_site_visitation": "INTEGER",
    "handwritten_reports": "INTEGER",
    "typed_reports": "INTEGER",
    "is_smoker": "INTEGER",
    "uses_vape": "INTEGER",
    "price_per_mile": "INTEGER",
    "driving_hourly_rate": "INTEGER",
    "charges_roundtrip_mileage": "INTEGER",
    "charges_roundtrip_driving_time": "INTEGER",
}


def extend_schema(connection):
    existing = {
        row[1]
        for row in connection.execute(
            "PRAGMA table_info(supervisors)"
        )
    }

    for field, field_type in PUBLIC_COLUMNS.items():
        if field not in existing:
            connection.execute(
                f"ALTER TABLE supervisors "
                f"ADD COLUMN {field} {field_type}"
            )
