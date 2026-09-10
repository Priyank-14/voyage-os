"""
Unit tests for ReplannerAgent and Minimal Replanning Principle.
"""
import pytest
from app.orchestration.state import TripGoal, DisruptionEvent
from app.agents.planner import planner_agent
from app.agents.replanner import replanner_agent


def test_minimal_replanning_preserves_unaffected_days():
    goal = TripGoal(
        destination="Rishikesh",
        duration_days=3,
        budget=15000.0,
        preferences=["adventure", "food"],
    )
    state = planner_agent.plan_trip(goal)

    # Record snapshot of Day 1 and Day 3
    day1_names_before = [a.name for a in state.itinerary.days[0].activities]
    day3_names_before = [a.name for a in state.itinerary.days[2].activities]
    day2_act1_before = state.itinerary.days[1].activities[0].name

    # Inject heavy rain on Day 2
    disruption = DisruptionEvent(
        event_type="WEATHER_RAIN",
        severity="HIGH",
        affected_day=2,
        description="Heavy rain on Day 2",
        probability=0.85,
    )

    decision = replanner_agent.replan_disrupted_activity(state, disruption)

    assert decision is not None
    assert len(state.decision_log) == 1

    # Verify Minimal Replanning: Day 1 and Day 3 are strictly identical!
    day1_names_after = [a.name for a in state.itinerary.days[0].activities]
    day3_names_after = [a.name for a in state.itinerary.days[2].activities]
    assert day1_names_before == day1_names_after
    assert day3_names_before == day3_names_after

    # Verify Day 2 Morning was replaced with an indoor activity
    day2_act1_after = state.itinerary.days[1].activities[0]
    assert day2_act1_after.name != day2_act1_before
    assert not day2_act1_after.is_outdoor
    assert day2_act1_after.status == "PLANNED"

    # Verify budget was updated correctly
    assert state.budget_remaining >= 0
