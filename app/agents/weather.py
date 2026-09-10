"""
Weather Agent for VoyageOS.
Evaluates destination forecasts against scheduled activities to detect meteorological threats.
"""
from typing import List, Dict, Any, Optional
from app.orchestration.state import TripState, DisruptionEvent
from app.tools.weather import weather_tool
from app.utils.logging import agent_logger
from app.utils.config import settings


class WeatherAgent:
    """Monitors and assesses weather conditions for scheduled trip days."""

    def __init__(self):
        self.name = "WEATHER_AGENT"

    def analyze_weather(
        self,
        state: TripState,
        injected_rain_day: Optional[int] = None,
        injected_rain_prob: float = 0.85,
        force_tool_failure: bool = False,
    ) -> List[DisruptionEvent]:
        """
        Fetches forecast and evaluates each outdoor activity.
        Returns a list of detected meteorological disruption events.
        """
        agent_logger.log(self.name, f"Fetching forecast for {state.goal.destination} ({state.goal.duration_days} days)")

        res = weather_tool.get_destination_forecast(
            destination=state.goal.destination,
            days=state.goal.duration_days,
            force_failure=force_tool_failure,
            injected_rain_day=injected_rain_day,
            injected_rain_prob=injected_rain_prob,
        )

        forecast_days = res.data.get("days", []) if res.data else []
        disruptions = []

        for forecast in forecast_days:
            day_num = forecast.get("day", 1)
            pop = forecast.get("precipitation_probability", 0.0)
            is_storm = forecast.get("is_storm", False)
            cond = forecast.get("condition", "Clear")

            agent_logger.log(
                self.name,
                f"Day {day_num} Forecast: {cond}, Rain Prob: {pop * 100:.0f}%, Temp: {forecast.get('temp_c')}°C",
            )

            # Check scheduled activities for this day
            day_plan = next((d for d in state.itinerary.days if d.day == day_num), None)
            if not day_plan:
                continue

            for act in day_plan.activities:
                if act.is_outdoor and (pop >= (settings.RAIN_DISRUPTION_THRESHOLD_PERCENT / 100.0) or is_storm):
                    severity = "HIGH" if pop >= 0.80 or is_storm else "MEDIUM"
                    event = DisruptionEvent(
                        event_type="WEATHER_RAIN",
                        severity=severity,
                        affected_day=day_num,
                        affected_activity_id=act.id,
                        description=(
                            f"Heavy precipitation alert ({pop * 100:.0f}%) detected on Day {day_num}. "
                            f"Threatens outdoor activity '{act.name}' ({act.category})."
                        ),
                        probability=pop,
                        status="DETECTED",
                    )
                    disruptions.append(event)
                    agent_logger.log(
                        self.name,
                        f"Disruption detected for '{act.name}' on Day {day_num}: Rain probability {pop * 100:.0f}%",
                        level="WARNING",
                        metadata={"activity_id": act.id, "severity": severity, "rain_prob": pop},
                    )

        return disruptions


weather_agent = WeatherAgent()
