"""
Deterministic policy rules for VoyageOS decision-making.
Enforces hard constraints, safety thresholds, and validation rules.
"""
from typing import Dict, Any, Tuple
from app.orchestration.state import Activity, DisruptionEvent
from app.utils.config import settings


class DecisionPolicies:
    """Enforces reproducible, deterministic hard constraints."""

    @staticmethod
    def should_trigger_weather_intervention(
        activity: Activity,
        precipitation_probability: float,
        is_storm: bool = False,
    ) -> Tuple[bool, str]:
        """
        Policy Rule:
        IF (precipitation_probability >= threshold OR is_storm) AND activity.is_outdoor == True
        THEN trigger_replanning
        """
        threshold = settings.RAIN_DISRUPTION_THRESHOLD_PERCENT / 100.0
        if not activity.is_outdoor:
            return False, "Activity is sheltered indoors; weather disruption does not impact safety."

        if is_storm:
            return True, f"Severe storm conditions detected; outdoor activity '{activity.name}' is unsafe."

        if precipitation_probability >= threshold:
            return True, (
                f"Rain probability ({precipitation_probability * 100:.0f}%) exceeds safety threshold "
                f"({settings.RAIN_DISRUPTION_THRESHOLD_PERCENT:.0f}%) for outdoor activity '{activity.name}'."
            )

        return False, f"Rain probability ({precipitation_probability * 100:.0f}%) is within acceptable safety bounds."

    @staticmethod
    def should_trigger_venue_intervention(activity: Activity, operating_status: str) -> Tuple[bool, str]:
        """
        Policy Rule:
        IF venue operating status is CLOSED or SUSPENDED
        THEN trigger_replanning
        """
        status_upper = operating_status.upper()
        if status_upper in ["CLOSED", "SUSPENDED", "UNAVAILABLE"]:
            return True, f"Venue for '{activity.name}' is currently {status_upper}."
        return False, f"Venue for '{activity.name}' is operating normally."

    @staticmethod
    def is_alternative_budget_viable(
        cost: float,
        current_activity_cost: float,
        remaining_budget: float,
    ) -> Tuple[bool, str]:
        """
        Policy Rule:
        New cost cannot exceed remaining_budget + current_activity_cost (budget released from cancellation).
        """
        effective_budget_available = remaining_budget + current_activity_cost
        if cost <= effective_budget_available:
            return True, f"Cost of ₹{cost:,.0f} is within available budget (₹{effective_budget_available:,.0f})."
        return False, (
            f"Cost of ₹{cost:,.0f} exceeds available budget of ₹{effective_budget_available:,.0f} "
            f"(overrun by ₹{cost - effective_budget_available:,.0f})."
        )
