"""
Planner Agent for VoyageOS.
Synthesizes trip goals into a structured, time-sequenced multi-day itinerary.
"""
from typing import List, Dict, Any, Optional
import uuid
from app.orchestration.state import TripGoal, TripState, Itinerary, DayPlan, Activity
from app.tools.places import places_tool
from app.utils.logging import agent_logger


class PlannerAgent:
    """Creates initial multi-day itineraries satisfying preferences and constraints."""

    def __init__(self):
        self.name = "PLANNER_AGENT"

    def plan_trip(self, goal: TripGoal) -> TripState:
        """
        Generates initial structured TripState from TripGoal.
        """
        agent_logger.log(self.name, f"Planning {goal.duration_days}-day trip to {goal.destination} (Budget: ₹{goal.budget:,.0f})")

        days: List[DayPlan] = []
        dest_lower = goal.destination.lower()

        if "rishikesh" in dest_lower:
            # Curated showcase plan for Rishikesh
            # Day 1: Arrival, Cafe & Scenic Trail
            d1_activities = [
                Activity(
                    id="act_d1_1",
                    day=1,
                    time_slot="Morning",
                    start_time="09:30",
                    end_time="12:00",
                    name="Artisanal Cafe Hopping in Tapovan",
                    category="food",
                    cost=950.0,
                    location="Upper Tapovan",
                    is_outdoor=False,
                    duration_hours=2.5,
                    disruption_risk="LOW",
                    weather_dependent=False,
                    status="PLANNED",
                ),
                Activity(
                    id="act_d1_2",
                    day=1,
                    time_slot="Afternoon",
                    start_time="13:30",
                    end_time="16:30",
                    name="Trek to Neer Garh Waterfall",
                    category="adventure",
                    cost=300.0,
                    location="Neer Garh",
                    is_outdoor=True,
                    duration_hours=3.0,
                    disruption_risk="HIGH",
                    weather_dependent=True,
                    status="PLANNED",
                ),
                Activity(
                    id="act_d1_3",
                    day=1,
                    time_slot="Evening",
                    start_time="17:30",
                    end_time="19:30",
                    name="Heritage Walk at The Beatles Ashram",
                    category="sightseeing",
                    cost=600.0,
                    location="Swarg Ashram",
                    is_outdoor=True,
                    duration_hours=2.0,
                    disruption_risk="MEDIUM",
                    weather_dependent=True,
                    status="PLANNED",
                ),
            ]
            days.append(DayPlan(day=1, activities=d1_activities))

            # Day 2: Flagship Adventure (River Rafting) & Cultural Sunset
            d2_activities = [
                Activity(
                    id="act_d2_1",
                    day=2,
                    time_slot="Morning",
                    start_time="09:00",
                    end_time="13:00",
                    name="River Rafting at Shivpuri (16 km)",
                    category="adventure",
                    cost=1500.0,
                    location="Shivpuri, Rishikesh",
                    is_outdoor=True,
                    duration_hours=4.0,
                    disruption_risk="HIGH",
                    weather_dependent=True,
                    status="PLANNED",
                ),
                Activity(
                    id="act_d2_2",
                    day=2,
                    time_slot="Afternoon",
                    start_time="14:00",
                    end_time="16:00",
                    name="Riverside Lunch & Relaxing at Laxman Jhula",
                    category="food",
                    cost=850.0,
                    location="Laxman Jhula",
                    is_outdoor=False,
                    duration_hours=2.0,
                    disruption_risk="LOW",
                    weather_dependent=False,
                    status="PLANNED",
                ),
                Activity(
                    id="act_d2_3",
                    day=2,
                    time_slot="Evening",
                    start_time="17:00",
                    end_time="19:00",
                    name="Ganga Aarti at Triveni Ghat",
                    category="culture",
                    cost=0.0,
                    location="Triveni Ghat",
                    is_outdoor=True,
                    duration_hours=2.0,
                    disruption_risk="MEDIUM",
                    weather_dependent=True,
                    status="PLANNED",
                ),
            ]
            days.append(DayPlan(day=2, activities=d2_activities))

            # Day 3: Gastronomy & Local Heritage
            d3_activities = [
                Activity(
                    id="act_d3_1",
                    day=3,
                    time_slot="Morning",
                    start_time="10:00",
                    end_time="12:30",
                    name="Tibetan Singing Bowl Sound Healing & Yin Yoga",
                    category="wellness",
                    cost=800.0,
                    location="Laxman Jhula road",
                    is_outdoor=False,
                    duration_hours=2.5,
                    disruption_risk="LOW",
                    weather_dependent=False,
                    status="PLANNED",
                ),
                Activity(
                    id="act_d3_2",
                    day=3,
                    time_slot="Afternoon",
                    start_time="13:00",
                    end_time="15:00",
                    name="Traditional Feast at Chotiwala",
                    category="food",
                    cost=650.0,
                    location="Ram Jhula",
                    is_outdoor=False,
                    duration_hours=2.0,
                    disruption_risk="LOW",
                    weather_dependent=False,
                    status="PLANNED",
                ),
                Activity(
                    id="act_d3_3",
                    day=3,
                    time_slot="Evening",
                    start_time="16:00",
                    end_time="18:00",
                    name="Local Craft Market & Souvenirs",
                    category="sightseeing",
                    cost=500.0,
                    location="Ram Jhula Market",
                    is_outdoor=False,
                    duration_hours=2.0,
                    disruption_risk="LOW",
                    weather_dependent=False,
                    status="PLANNED",
                ),
            ]
            days.append(DayPlan(day=3, activities=d3_activities))

        else:
            # Generic itinerary builder
            catalog = places_tool.get_activities_for_destination(goal.destination).data or []
            for d in range(1, goal.duration_days + 1):
                day_acts = []
                for slot, idx in [("Morning", 0), ("Afternoon", 1), ("Evening", 2)]:
                    cat_item = catalog[idx % len(catalog)] if catalog else {}
                    day_acts.append(
                        Activity(
                            id=f"act_d{d}_{slot.lower()}",
                            day=d,
                            time_slot=slot,
                            name=cat_item.get("name", f"{slot} activity in {goal.destination}"),
                            category=cat_item.get("category", "sightseeing"),
                            cost=cat_item.get("cost", 500.0),
                            location=cat_item.get("location", goal.destination),
                            is_outdoor=cat_item.get("is_outdoor", True),
                            duration_hours=cat_item.get("duration_hours", 2.0),
                            disruption_risk=cat_item.get("disruption_risk", "LOW"),
                            weather_dependent=cat_item.get("weather_dependent", True),
                            status="PLANNED",
                        )
                    )
                days.append(DayPlan(day=d, activities=day_acts))

        itinerary = Itinerary(days=days[:goal.duration_days])
        state = TripState(
            goal=goal,
            budget_total=goal.budget,
            itinerary=itinerary,
            status="PLANNED",
        )
        state.recalculate_budget()

        # Save initial snapshot for before/after comparison
        state.itinerary_history.append({
            "stage": "initial_plan",
            "timestamp": "00:00:00",
            "snapshot": itinerary.model_dump(),
        })

        agent_logger.log(
            self.name,
            f"Initial itinerary generated: {len(itinerary.all_activities)} activities, "
            f"Projected Spend: ₹{state.budget_used:,.0f}, Remaining: ₹{state.budget_remaining:,.0f}",
        )
        return state


planner_agent = PlannerAgent()
