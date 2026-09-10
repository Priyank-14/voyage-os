"""
Validation utilities for VoyageOS input sanitization and verification.
"""
from typing import List, Dict, Any, Tuple


def validate_trip_input(
    destination: str,
    duration_days: int,
    budget: float,
    preferences: List[str],
) -> Tuple[bool, List[str]]:
    """
    Validates trip creation parameters.
    Returns (is_valid, error_messages).
    """
    errors = []

    if not destination or not destination.strip():
        errors.append("Destination cannot be empty.")

    if duration_days <= 0:
        errors.append("Duration must be at least 1 day.")
    elif duration_days > 14:
        errors.append("Duration exceeds prototype maximum of 14 days.")

    if budget <= 0:
        errors.append("Budget must be a positive number.")
    elif budget < (duration_days * 1000):
        errors.append(
            f"Budget of ₹{budget:,.0f} is unrealistically low for {duration_days} days (min recommended: ₹{duration_days * 1000:,.0f})."
        )

    if not preferences or len(preferences) == 0:
        errors.append("At least one travel preference must be specified.")

    return len(errors) == 0, errors
