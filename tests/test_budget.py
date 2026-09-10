"""
Unit tests for BudgetAgent.
Tests tracking, budget exhaustion protection, and replacement viability checks.
"""
import pytest
from app.orchestration.state import TripGoal
from app.agents.planner import planner_agent
from app.agents.budget import budget_agent


def test_budget_audit_calculation():
    goal = TripGoal(
        destination="Rishikesh",
        duration_days=3,
        budget=15000.0,
        preferences=["adventure"],
    )
    state = planner_agent.plan_trip(goal)
    audit = budget_agent.audit_budget(state)

    assert audit["total"] == 15000.0
    assert audit["used"] == state.itinerary.total_cost
    assert audit["remaining"] == (15000.0 - state.itinerary.total_cost)
    assert audit["status"] in ["HEALTHY", "WARNING"]


def test_budget_rejects_excessive_alternative():
    goal = TripGoal(
        destination="Rishikesh",
        duration_days=3,
        budget=7000.0,
        preferences=["adventure"],
    )
    state = planner_agent.plan_trip(goal)
    # Trip uses 6150 out of 7000 => remaining is 850
    # Old activity cost: 1500
    # Allowable = 850 + 1500 = 2350
    # A candidate costing 5000 should be rejected!
    is_viable, delta, msg = budget_agent.evaluate_cost_change(
        state=state,
        old_cost=1500.0,
        new_cost=5000.0,
    )
    assert not is_viable
    assert "exceeds" in msg.lower()


def test_budget_accepts_cost_saving_alternative():
    goal = TripGoal(
        destination="Rishikesh",
        duration_days=3,
        budget=15000.0,
        preferences=["adventure"],
    )
    state = planner_agent.plan_trip(goal)
    # Old activity: 1500, new activity: 900
    is_viable, delta, msg = budget_agent.evaluate_cost_change(
        state=state,
        old_cost=1500.0,
        new_cost=900.0,
    )
    assert is_viable
    assert delta == -600.0
