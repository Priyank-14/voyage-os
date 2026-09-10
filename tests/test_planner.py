"""
Unit tests for PlannerAgent.
Tests goal interpretation, structured itinerary generation, and budget constraints.
"""
import pytest
from app.orchestration.state import TripGoal
from app.agents.planner import planner_agent


def test_planner_creates_itinerary_with_correct_days():
    goal = TripGoal(
        destination="Rishikesh",
        duration_days=3,
        budget=15000.0,
        preferences=["adventure", "food"],
    )
    state = planner_agent.plan_trip(goal)

    assert state.goal.destination == "Rishikesh"
    assert len(state.itinerary.days) == 3
    assert len(state.itinerary.all_activities) >= 6
    assert state.budget_total == 15000.0
    assert state.budget_used <= state.budget_total
    assert state.budget_remaining >= 0


def test_planner_allocates_daily_activities():
    goal = TripGoal(
        destination="Rishikesh",
        duration_days=3,
        budget=15000.0,
        preferences=["adventure", "food"],
    )
    state = planner_agent.plan_trip(goal)

    for day in state.itinerary.days:
        assert len(day.activities) == 3
        time_slots = [a.time_slot for a in day.activities]
        assert "Morning" in time_slots
        assert "Afternoon" in time_slots
        assert "Evening" in time_slots


def test_planner_generic_destination():
    goal = TripGoal(
        destination="Jaipur",
        duration_days=2,
        budget=10000.0,
        preferences=["culture"],
    )
    state = planner_agent.plan_trip(goal)

    assert state.goal.destination == "Jaipur"
    assert len(state.itinerary.days) == 2
    assert state.budget_used <= 10000.0
