"""
Unit tests for DecisionEngine and deterministic policies.
"""
import pytest
from app.orchestration.state import Activity, DisruptionEvent
from app.decision.policies import DecisionPolicies
from app.decision.engine import decision_engine


def test_weather_policy_triggers_on_high_rain_for_outdoor():
    act = Activity(
        day=2,
        name="River Rafting",
        category="adventure",
        cost=1500.0,
        is_outdoor=True,
    )
    # Rain prob 85% >= 70% threshold
    should_intervene, reason = DecisionPolicies.should_trigger_weather_intervention(
        activity=act,
        precipitation_probability=0.85,
    )
    assert should_intervene
    assert "exceeds safety threshold" in reason


def test_weather_policy_bypasses_indoor_activity():
    act = Activity(
        day=2,
        name="Indoor Climbing",
        category="adventure",
        cost=900.0,
        is_outdoor=False,
    )
    # Even with 95% rain, indoor activity is safe
    should_intervene, reason = DecisionPolicies.should_trigger_weather_intervention(
        activity=act,
        precipitation_probability=0.95,
    )
    assert not should_intervene
    assert "sheltered indoors" in reason


def test_decision_engine_evaluates_venue_closure():
    act = Activity(
        day=1,
        name="Beatles Ashram",
        category="sightseeing",
        cost=600.0,
    )
    event = DisruptionEvent(
        event_type="VENUE_CLOSED",
        severity="HIGH",
        affected_day=1,
        affected_activity_id=act.id,
        description="Ashram closed for maintenance",
        probability=1.0,
    )
    should_intervene, reason, evidence = decision_engine.evaluate_disruption(
        event=event,
        affected_activity=act,
        trip_remaining_budget=5000.0,
    )
    assert should_intervene
    assert evidence["operating_status"] == "CLOSED"
