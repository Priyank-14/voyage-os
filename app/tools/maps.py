"""
Mobility and Mapping tool adapter for VoyageOS.
Calculates distances, transit times, and road conditions between locations.
"""
from typing import Dict, Any, Optional
import math
from app.tools.fallback import execute_with_resilience, ToolCallResult
from app.utils.config import settings


class MapsTool:
    """Calculates route transit times and distances with resilient fallback."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GOOGLE_MAPS_API_KEY

    def calculate_transit(
        self,
        origin: str,
        destination: str,
        mode: str = "driving",
        force_failure: bool = False,
        simulated_traffic_factor: float = 1.0,
    ) -> ToolCallResult:
        """
        Calculates distance and travel time between two points.
        Includes simulated traffic factor (e.g., 1.5 for landslide/heavy traffic).
        """
        def _primary_api() -> Dict[str, Any]:
            if not self.api_key:
                raise ConnectionError("No Maps API key configured.")
            # Placeholder for Google Maps Distance Matrix or OSRM
            raise ConnectionError("Maps service connection timed out.")

        def _fallback_provider() -> Dict[str, Any]:
            # Deterministic distance estimation based on known spot distances or heuristic
            key = f"{origin.lower()}->{destination.lower()}"
            
            # Curated popular routes in Rishikesh / typical destinations
            known_distances = {
                "tapovan->shivpuri": (16.0, 35),
                "shivpuri->tapovan": (16.0, 35),
                "tapovan->laxman jhula": (2.5, 10),
                "laxman jhula->ram jhula": (2.0, 8),
                "tapovan->beatles ashram": (4.5, 18),
                "beatles ashram->triveni ghat": (5.0, 20),
                "tapovan->neer garh waterfall": (6.0, 20),
                "tapovan->kunjapuri": (26.0, 55),
            }

            matched = None
            for k, val in known_distances.items():
                if k in key or key in k:
                    matched = val
                    break

            if matched:
                distance_km, base_duration_mins = matched
            else:
                # Default reasonable transit heuristic
                distance_km = 5.0
                base_duration_mins = 15

            duration_mins = int(base_duration_mins * simulated_traffic_factor)

            return {
                "origin": origin,
                "destination": destination,
                "mode": mode,
                "distance_km": round(distance_km, 1),
                "duration_mins": duration_mins,
                "traffic_delay_mins": max(0, duration_mins - base_duration_mins),
                "road_status": "CONGESTED" if simulated_traffic_factor > 1.4 else "CLEAR",
            }

        return execute_with_resilience(
            primary_fn=_primary_api,
            fallback_fn=_fallback_provider,
            tool_name="MAPS_TOOL",
            force_failure=force_failure or (not self.api_key),
        )


maps_tool = MapsTool()
