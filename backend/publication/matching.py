"""Match acquired listings to verified provider registrations."""

import re


def normalize_email(value):
    return (value or "").strip().lower()


def normalize_phone(value):
    digits = re.sub(r"[^0-9]", "", value or "")

    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]

    return digits if len(digits) == 10 else ""


def matches_registration(acquired, registration):
    acquired_email = normalize_email(acquired.get("email"))
    account_email = normalize_email(
        registration.get("account_email")
    )

    if (
        registration.get("email_verified_at")
        and acquired_email
        and acquired_email == account_email
    ):
        return True

    if registration.get("phone_verified_at"):
        acquired_phone = normalize_phone(acquired.get("phone"))
        registered_phone = normalize_phone(registration.get("phone"))

        if acquired_phone and acquired_phone == registered_phone:
            return True

    return False
