"""
Weather Tool adapter for VoyageOS.
Connects to OpenWeatherMap API with automatic failover to local meteorological simulation.
"""
from typing import Dict, Any, Optional
import requests
from app.tools.fallback import execute_with_resilience, ToolCallResult
from app.utils.config import settings
from app.utils.logging import agent_logger


class WeatherTool:
    """Provides structured weather forecast data with fallback recovery."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.OPENWEATHER_API_KEY

    def get_destination_forecast(
        self,
        destination: str,
        days: int = 3,
        force_failure: bool = False,
        injected_rain_day: Optional[int] = None,
        injected_rain_prob: float = 0.85,
    ) -> ToolCallResult:
        """
        Retrieves weather forecast for a destination.
        If force_failure is True, simulates an API timeout to trigger fallback.
        """
        def _primary_api() -> Dict[str, Any]:
            if not self.api_key:
                raise ConnectionError("No OpenWeatherMap API key configured.")
            
            url = f"https://api.openweathermap.org/data/2.5/forecast?q={destination}&appid={self.api_key}&units=metric"
            resp = requests.get(url, timeout=3.0)
            if resp.status_code != 200:
                raise ConnectionError(f"Weather API returned status code {resp.status_code}")
            
            raw = resp.json()
            # Parse daily aggregates from 3-hour slices
            daily_forecasts = {}
            for item in raw.get("list", [])[: days * 8]:
                dt_txt = item.get("dt_txt", "")
                date_str = dt_txt.split(" ")[0]
                if date_str not in daily_forecasts:
                    pop = item.get("pop", 0.0)  # Probability of precipitation
                    temp = item.get("main", {}).get("temp", 24.0)
                    desc = item.get("weather", [{}])[0].get("description", "clear sky")
                    daily_forecasts[date_str] = {
                        "temp_c": temp,
                        "precipitation_probability": pop,
                        "condition": desc,
                        "is_storm": "storm" in desc.lower() or "heavy" in desc.lower(),
                    }
            return {
                "destination": destination,
                "days": list(daily_forecasts.values())[:days],
            }

        def _fallback_provider() -> Dict[str, Any]:
            """Deterministic meteorological baseline data with support for injected conditions."""
            forecasts = []
            dest_lower = destination.lower()

            base_temp = 26.0
            base_condition = "Partly Cloudy"
            base_pop = 0.15

            if "rishikesh" in dest_lower:
                base_temp = 24.0
            elif "manali" in dest_lower:
                base_temp = 14.0
            elif "goa" in dest_lower:
                base_temp = 30.0

            for d in range(1, days + 1):
                pop = base_pop
                cond = base_condition
                temp = base_temp + (d * 0.5)

                # Check if this day has an injected weather event
                if injected_rain_day == d:
                    pop = injected_rain_prob
                    cond = "Heavy Rain & Mountain Thunderstorms"

                forecasts.append({
                    "day": d,
                    "temp_c": round(temp, 1),
                    "precipitation_probability": round(pop, 2),
                    "condition": cond,
                    "is_storm": pop > 0.70,
                    "wind_speed_kmh": 18.5 if pop > 0.70 else 8.2,
                })

            return {
                "destination": destination,
                "days": forecasts,
            }

        return execute_with_resilience(
            primary_fn=_primary_api,
            fallback_fn=_fallback_provider,
            tool_name="WEATHER_TOOL",
            force_failure=force_failure or (not self.api_key),
        )


weather_tool = WeatherTool()
