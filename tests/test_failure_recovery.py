"""
Unit tests for external tool resilience, API failure handling, and fallback recovery.
"""
import pytest
from app.tools.weather import weather_tool
from app.tools.maps import maps_tool
from app.tools.fallback import execute_with_resilience


def test_weather_tool_recovers_from_api_failure():
    # Force primary failure to simulate an external network outage
    res = weather_tool.get_destination_forecast(
        destination="Rishikesh",
        days=3,
        force_failure=True,
    )
    assert res.status == "recovered"
    assert res.source == "fallback"
    assert res.data is not None
    assert len(res.data["days"]) == 3
    assert res.data["destination"] == "Rishikesh"


def test_maps_tool_recovers_from_transit_failure():
    res = maps_tool.calculate_transit(
        origin="Tapovan",
        destination="Shivpuri",
        force_failure=True,
    )
    assert res.status == "recovered"
    assert res.source == "fallback"
    assert res.data["distance_km"] > 0
    assert res.data["duration_mins"] > 0


def test_execute_with_resilience_circuit_breaker():
    def failing_primary():
        raise ConnectionResetError("Connection lost to external provider")

    def reliable_fallback():
        return {"result": "safe_cached_data"}

    result = execute_with_resilience(
        primary_fn=failing_primary,
        fallback_fn=reliable_fallback,
        tool_name="TEST_SERVICE",
        max_retries=1,
    )

    assert result.status == "recovered"
    assert result.source == "fallback"
    assert result.data["result"] == "safe_cached_data"
