"""
Database schema representations and serialization helpers for SQLite.
"""
from typing import Dict, Any
import json
from app.orchestration.state import TripState, TripGoal, Itinerary, DisruptionEvent, DecisionRecord


def serialize_trip_state(state: TripState) -> Dict[str, Any]:
    """Serializes a TripState instance into a dictionary suitable for SQLite storage."""
    return {
        "trip_id": state.trip_id,
        "created_at": state.created_at,
        "destination": state.goal.destination,
        "duration_days": state.goal.duration_days,
        "budget_total": state.budget_total,
        "budget_used": state.budget_used,
        "budget_remaining": state.budget_remaining,
        "goal_json": state.goal.model_dump_json(),
        "itinerary_json": state.itinerary.model_dump_json(),
        "disruptions_json": json.dumps([d.model_dump() for d in state.active_disruptions]),
        "decisions_json": json.dumps([d.model_dump() for d in state.decision_log]),
        "history_json": json.dumps(state.itinerary_history),
        "status": state.status,
    }


def deserialize_trip_state(row: Dict[str, Any]) -> TripState:
    """Deserializes a SQLite row dictionary into a full TripState model."""
    goal = TripGoal.model_validate_json(row["goal_json"])
    itinerary = Itinerary.model_validate_json(row["itinerary_json"])
    disruptions = [DisruptionEvent.model_validate(d) for d in json.loads(row["disruptions_json"])]
    decisions = [DecisionRecord.model_validate(d) for d in json.loads(row["decisions_json"])]
    history = json.loads(row["history_json"])

    return TripState(
        trip_id=row["trip_id"],
        created_at=row["created_at"],
        goal=goal,
        budget_total=row["budget_total"],
        budget_used=row["budget_used"],
        budget_remaining=row["budget_remaining"],
        itinerary=itinerary,
        active_disruptions=disruptions,
        decision_log=decisions,
        itinerary_history=history,
        status=row["status"],
    )
