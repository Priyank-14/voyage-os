"""
Structured state models for VoyageOS.
Provides typed Pydantic models for goals, activities, itinerary snapshots,
disruptions, decision logs, and full trip state.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from pydantic import BaseModel, Field


class TripGoal(BaseModel):
    destination: str
    duration_days: int = Field(ge=1, le=14)
    budget: float = Field(gt=0)
    preferences: List[str] = Field(default_factory=list)
    must_visit: List[str] = Field(default_factory=list)
    avoidances: List[str] = Field(default_factory=list)
    constraints: Dict[str, Any] = Field(default_factory=dict)


class Activity(BaseModel):
    id: str = Field(default_factory=lambda: f"act_{uuid.uuid4().hex[:8]}")
    day: int = Field(ge=1)
    time_slot: str = "Morning"  # Morning, Afternoon, Evening
    start_time: str = "10:00"
    end_time: str = "12:00"
    name: str
    category: str = "sightseeing"  # adventure, food, sightseeing, wellness, culture
    cost: float = 0.0
    location: str = ""
    is_outdoor: bool = True
    duration_hours: float = 2.0
    disruption_risk: str = "LOW"  # HIGH, MEDIUM, LOW
    weather_dependent: bool = True
    status: str = "PLANNED"  # PLANNED, COMPLETED, DISRUPTED, REPLACED
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DayPlan(BaseModel):
    day: int
    activities: List[Activity] = Field(default_factory=list)

    @property
    def day_cost(self) -> float:
        return sum(a.cost for a in self.activities if a.status != "REPLACED")


class Itinerary(BaseModel):
    days: List[DayPlan] = Field(default_factory=list)

    @property
    def total_cost(self) -> float:
        return sum(d.day_cost for d in self.days)

    @property
    def all_activities(self) -> List[Activity]:
        acts = []
        for d in self.days:
            acts.extend(d.activities)
        return acts

    def get_activity_by_id(self, activity_id: str) -> Optional[Activity]:
        for d in self.days:
            for a in d.activities:
                if a.id == activity_id:
                    return a
        return None


class DisruptionEvent(BaseModel):
    id: str = Field(default_factory=lambda: f"dis_{uuid.uuid4().hex[:8]}")
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))
    event_type: str = "WEATHER_RAIN"  # WEATHER_RAIN, VENUE_CLOSED, MOBILITY_DELAY, BUDGET_OVERRUN
    severity: str = "HIGH"  # HIGH, MEDIUM, LOW
    affected_day: int
    affected_activity_id: Optional[str] = None
    description: str
    probability: float = 1.0
    status: str = "DETECTED"  # DETECTED, EVALUATING, RESOLVED, IGNORED


class DecisionRecord(BaseModel):
    id: str = Field(default_factory=lambda: f"dec_{uuid.uuid4().hex[:8]}")
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))
    agent_name: str
    trigger: str
    action_taken: str
    rationale: str
    evidence: Dict[str, Any] = Field(default_factory=dict)
    affected_items: List[str] = Field(default_factory=list)
    alternative_selected: Optional[Dict[str, Any]] = None


class TripState(BaseModel):
    trip_id: str = Field(default_factory=lambda: f"trip_{uuid.uuid4().hex[:8]}")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    goal: TripGoal
    budget_total: float
    budget_used: float = 0.0
    budget_remaining: float = 0.0
    itinerary: Itinerary = Field(default_factory=Itinerary)
    active_disruptions: List[DisruptionEvent] = Field(default_factory=list)
    decision_log: List[DecisionRecord] = Field(default_factory=list)
    itinerary_history: List[Dict[str, Any]] = Field(default_factory=list)
    status: str = "PLANNED"  # PLANNED, MONITORING, REPLANNING, ADAPTED, COMPLETED

    def recalculate_budget(self):
        self.budget_used = self.itinerary.total_cost
        self.budget_remaining = self.budget_total - self.budget_used
