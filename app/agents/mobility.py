"""
Mobility and Navigation Agent for VoyageOS.
Evaluates inter-activity transit times, route viability, and mobility disruptions.
"""
from typing import List, Dict, Any, Optional
from app.orchestration.state import TripState, DisruptionEvent
from app.tools.maps import maps_tool
from app.utils.logging import agent_logger


class MobilityAgent:
    """Tracks transit schedules and detects mobility bottlenecks."""

    def __init__(self):
        self.name = "MOBILITY_AGENT"

    def audit_itinerary_transit(
        self, state: TripState, simulated_traffic_factor: float = 1.0
    ) -> Dict[str, Any]:
        """
        Calculates transit between consecutive activities on each day.
        """
        agent_logger.log(self.name, "Auditing inter-activity transit times and routes")
        day_transit_metrics = []
        total_transit_mins = 0

        for day in state.itinerary.days:
            acts = [a for a in day.activities if a.status != "REPLACED"]
            day_mins = 0
            legs = []

            for i in range(len(acts) - 1):
                orig = acts[i].location or state.goal.destination
                dest = acts[i + 1].location or state.goal.destination
                res = maps_tool.calculate_transit(
                    origin=orig,
                    destination=dest,
                    simulated_traffic_factor=simulated_traffic_factor,
                )
                leg_data = res.data or {"duration_mins": 15, "distance_km": 4.0}
                day_mins += leg_data.get("duration_mins", 15)
                legs.append({
                    "from": acts[i].name,
                    "to": acts[i + 1].name,
                    "transit_mins": leg_data.get("duration_mins", 15),
                    "distance_km": leg_data.get("distance_km", 4.0),
                    "road_status": leg_data.get("road_status", "CLEAR"),
                })

            total_transit_mins += day_mins
            day_transit_metrics.append({
                "day": day.day,
                "transit_mins": day_mins,
                "legs": legs,
            })

        agent_logger.log(self.name, f"Transit audit complete: {total_transit_mins} total transit minutes across {len(state.itinerary.days)} days")
        return {
            "total_transit_mins": total_transit_mins,
            "days": day_transit_metrics,
        }

    def check_transit_disruptions(
        self, state: TripState, traffic_spike_day: Optional[int] = None
    ) -> List[DisruptionEvent]:
        """
        Checks for high traffic delays or road closures.
        """
        disruptions = []
        if traffic_spike_day:
            event = DisruptionEvent(
                event_type="MOBILITY_DELAY",
                severity="HIGH",
                affected_day=traffic_spike_day,
                description=f"Severe mountain highway congestion/delay detected on Day {traffic_spike_day}.",
                probability=0.90,
                status="DETECTED",
            )
            disruptions.append(event)
            agent_logger.log(
                self.name,
                f"Mobility disruption detected on Day {traffic_spike_day}: severe highway congestion",
                level="WARNING",
            )
        return disruptions


mobility_agent = MobilityAgent()
