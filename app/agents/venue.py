"""
Venue and Activity Agent for VoyageOS.
Audits venue operating status, manages activity discovery, and surfaces candidates for replanning.
"""
from typing import List, Dict, Any, Optional
from app.orchestration.state import TripState, DisruptionEvent, Activity
from app.tools.places import places_tool
from app.utils.logging import agent_logger


class VenueAgent:
    """Monitors activity operational readiness and supplies alternative candidates."""

    def __init__(self):
        self.name = "VENUE_AGENT"

    def audit_venues(
        self, state: TripState, closed_activity_id: Optional[str] = None
    ) -> List[DisruptionEvent]:
        """
        Audits all activities in the itinerary for operational closures.
        """
        agent_logger.log(self.name, "Auditing operational readiness of planned venues")
        disruptions = []

        for day in state.itinerary.days:
            for act in day.activities:
                if act.status == "REPLACED":
                    continue

                is_closed = (act.id == closed_activity_id)
                if is_closed:
                    event = DisruptionEvent(
                        event_type="VENUE_CLOSED",
                        severity="HIGH",
                        affected_day=day.day,
                        affected_activity_id=act.id,
                        description=f"Venue '{act.name}' has announced unexpected maintenance/closure.",
                        probability=1.0,
                        status="DETECTED",
                    )
                    disruptions.append(event)
                    agent_logger.log(
                        self.name,
                        f"Venue closure detected for '{act.name}' (ID: {act.id}) on Day {day.day}",
                        level="WARNING",
                    )

        return disruptions

    def find_alternatives(
        self,
        destination: str,
        must_be_indoor: bool = False,
        preferred_category: Optional[str] = None,
        max_cost: Optional[float] = None,
        current_activity_ids: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Finds candidate alternatives from the catalog filtered by constraints.
        """
        agent_logger.log(
            self.name,
            f"Searching alternatives for {destination} (indoor_only={must_be_indoor}, max_cost={max_cost})",
        )
        candidates = places_tool.search_alternatives(
            destination=destination,
            must_be_indoor=must_be_indoor,
            preferred_category=preferred_category,
            max_cost=max_cost,
            exclude_activity_ids=current_activity_ids,
        )
        agent_logger.log(self.name, f"Found {len(candidates)} viable candidate alternatives")
        return candidates


venue_agent = VenueAgent()
