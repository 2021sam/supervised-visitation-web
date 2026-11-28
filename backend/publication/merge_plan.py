"""Determine registration overrides without modifying databases."""

from backend.publication.matching import matches_registration
from backend.publication.registration_status import publication_action


def build_merge_plan(acquired, registrations):
    plan = []
    claimed = set()

    for registration in registrations:
        action = publication_action(registration)

        if action == "ignore":
            continue

        matched_ids = sorted(
            row["supervisor_id"]
            for row in acquired
            if matches_registration(row, registration)
        )

        if claimed.intersection(matched_ids):
            raise ValueError(
                "Conflicting registrations match an acquired listing."
            )

        claimed.update(matched_ids)

        plan.append({
            "registration": registration,
            "action": action,
            "matched_ids": matched_ids,
        })

    return plan
