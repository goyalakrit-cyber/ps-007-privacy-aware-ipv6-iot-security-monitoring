from datetime import timedelta
from typing import Any


def inspect_rotation(
    events: list[dict[str, Any]],
    window_minutes: int = 15,
    rotation_threshold: int = 2,
) -> list[dict[str, Any]]:
    """Flag repeated address-fingerprint changes within a short time window."""
    if not events:
        return []

    latest = max(event["observed_at"] for event in events)
    cutoff = latest - timedelta(minutes=window_minutes)
    recent = [event for event in events if event["observed_at"] >= cutoff]
    if not recent:
        return []

    ordered = sorted(recent, key=lambda event: event["observed_at"])
    rotations = sum(
        previous["ipv6_address"] != current["ipv6_address"]
        for previous, current in zip(ordered, ordered[1:])
    )
    if rotations < rotation_threshold:
        return []

    return [
        {
            "device_key": ordered[-1]["device_id"],
            "severity": "medium",
            "title": "Rapid IPv6 Rotation Detected",
            "description": (
                f"Device changed address {rotations} times within "
                f"{window_minutes} minutes."
            ),
            "score": 7.5,
        }
    ]
