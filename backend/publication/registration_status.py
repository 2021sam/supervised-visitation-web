"""Determine how a registration affects the public directory."""


def publication_action(registration):
    status = registration.get("status")

    if status == "active":
        return "publish"

    if status == "deleted":
        return "suppress"

    if status == "hidden":
        if registration.get("last_published_at"):
            return "suppress"

        return "ignore"

    raise ValueError(f"Unknown registration status: {status}")
