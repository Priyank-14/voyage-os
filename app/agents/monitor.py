"""
Monitoring Agent for VoyageOS.
Autonomously surveys environmental signals (weather, transit, venue status) and injects disruption alerts.
"""
from typing import List, Optional
from app.orchestration.state import TripState, DisruptionEvent
from app.agents.weather import weather_agent
from app.agents.venue import venue_agent
from app.agents.mobility import mobility_agent
from app.utils.logging import agent_logger


class MonitoringAgent:
    """Continuous monitor assessing real-world and simulated signals."""

    def __init__(self):
        self.name = "MONITOR_AGENT"

    def scan_environment(
        self,
        state: TripState,
        simulated_weather_day: Optional[int] = None,
        simulated_weather_prob: float = 0.85,
        simulated_closed_venue_id: Optional[str] = None,
        simulated_traffic_day: Optional[int] = None,
        force_weather_failure: bool = False,
    ) -> List[DisruptionEvent]:
        """
        Polls specialized perception agents and compiles active disruption events.
        """
        agent_logger.log(self.name, f"Initiating autonomous environmental scan for trip {state.trip_id}")
        detected_events: List[DisruptionEvent] = []

        # 1. Weather scan
        weather_events = weather_agent.analyze_weather(
            state=state,
            injected_rain_day=simulated_weather_day,
            injected_rain_prob=simulated_weather_prob,
            force_tool_failure=force_weather_failure,
        )
        detected_events.extend(weather_events)

        # 2. Venue closures scan
        venue_events = venue_agent.audit_venues(
            state=state,
            closed_activity_id=simulated_closed_venue_id,
        )
        detected_events.extend(venue_events)

        # 3. Mobility delays scan
        mobility_events = mobility_agent.check_transit_disruptions(
            state=state,
            traffic_spike_day=simulated_traffic_day,
        )
        detected_events.extend(mobility_events)

        if detected_events:
            agent_logger.log(
                self.name,
                f"Scan detected {len(detected_events)} environmental disruption(s)",
                level="WARNING",
            )
        else:
            agent_logger.log(self.name, "All monitored signals stable; conditions clear", level="INFO")

        return detected_events


monitoring_agent = MonitoringAgent()
