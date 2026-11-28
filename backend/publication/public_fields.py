"""Select information permitted in public provider listings."""

from backend.publication.schema import PUBLIC_COLUMNS

CONTACT_FIELDS = (
    "phone",
    "email",
    "website",
    "address",
)

PUBLIC_FIELDS = (
    "city",
    "state_code",
    "zip_code",
    "service_area",
    "service_counties",
    "languages",
    "additional_info",
)


def public_profile(registration):
    name = " ".join(
        str(registration.get(field) or "").strip()
        for field in ("first_name", "middle_name", "last_name")
        if registration.get(field)
    ).strip()

    if registration.get("provider_type") == "agency":
        name = registration.get("business_name") or name

    result = {"name": name}

    for field in PUBLIC_FIELDS:
        result[field] = registration.get(field) or ""

    for field in CONTACT_FIELDS:
        result[field] = (
            registration.get(field) or ""
            if registration.get(f"{field}_visibility") == "public"
            else ""
        )

    for field in PUBLIC_COLUMNS:
        result[field] = registration.get(field)

    if registration.get("calendar_visibility") != "public":
        result["calendar_url"] = None

    if not result["phone"]:
        result["phone_is_cell"] = None

    return result
