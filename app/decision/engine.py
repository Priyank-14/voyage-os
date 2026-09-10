"""
Decision Engine for VoyageOS.
Evaluates detected disruptions against deterministic safety and constraint policies
to determine whether intervention and itinerary modification are required.
"""
from typing import Tuple, Optional, Dict, Any
from app.orchestration.state import Activity, DisruptionEvent, DecisionRecord
from app.decision.policies import DecisionPolicies
from app.decision.scoring import alternative_scorer
from app.utils.logging import agent_logger


class DecisionEngine:
    """Evaluates conflicts and decides whether replanning is warranted."""

    def evaluate_disruption(
        self,
        event: DisruptionEvent,
        affected_activity: Optional[Activity],
        trip_remaining_budget: float,
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Evaluates a DisruptionEvent and returns:
        (requires_intervention, rationale, evidence_dict)
        """
        agent_logger.log("DECISION_ENGINE", f"Evaluating event {event.event_type} on Day {event.affected_day}")

        if not affected_activity:
            return False, "No specific activity affected by disruption.", {}

        # 1. Weather Disruption Evaluation
        if "WEATHER" in event.event_type:
            should_intervene, reason = DecisionPolicies.should_trigger_weather_intervention(
                activity=affected_activity,
                precipitation_probability=event.probability,
                is_storm=event.severity == "HIGH",
            )
            evidence = {
                "event_type": event.event_type,
                "activity_name": affected_activity.name,
                "is_outdoor": affected_activity.is_outdoor,
                "probability": event.probability,
                "severity": event.severity,
                "policy_triggered": should_intervene,
            }
            if should_intervene:
                agent_logger.log(
                    "DECISION_ENGINE",
                    f"Intervention triggered: {reason}",
                    level="WARNING",
                    metadata=evidence,
                )
            else:
                agent_logger.log("DECISION_ENGINE", f"No intervention needed: {reason}", level="INFO")
            return should_intervene, reason, evidence

        # 2. Venue Closure Evaluation
        if "VENUE" in event.event_type:
            should_intervene, reason = DecisionPolicies.should_trigger_venue_intervention(
                activity=affected_activity,
                operating_status="CLOSED",
            )
            evidence = {
                "event_type": event.event_type,
                "activity_name": affected_activity.name,
                "operating_status": "CLOSED",
                "policy_triggered": should_intervene,
            }
            return should_intervene, reason, evidence

        # 3. Mobility Delay Evaluation
        if "MOBILITY" in event.event_type:
            should_intervene = event.severity in ["HIGH", "CRITICAL"]
            reason = f"Mobility transit delay severity '{event.severity}' requires schedule realignment."
            evidence = {"event_type": event.event_type, "severity": event.severity}
            return should_intervene, reason, evidence

        # Default fallback
        return False, "Disruption event does not violate hard constraints.", {}


decision_engine = DecisionEngine()
