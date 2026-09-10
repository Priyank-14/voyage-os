"""
Critic and Evaluation Agent for VoyageOS.
Conducts multi-dimensional evaluations across budget, weather, travel time, preferences, and constraints.
"""
from typing import Dict, Any, List
from app.orchestration.state import TripState, DisruptionEvent
from app.agents.budget import budget_agent
from app.utils.logging import agent_logger


class CriticResult:
    def __init__(
        self,
        budget_pass: bool,
        weather_pass: bool,
        travel_pass: bool,
        preference_pass: bool,
        details: Dict[str, Any],
        verdict: str,  # "PASS" or "REPLAN_REQUIRED"
        issues: List[str],
    ):
        self.budget_pass = budget_pass
        self.weather_pass = weather_pass
        self.travel_pass = travel_pass
        self.preference_pass = preference_pass
        self.details = details
        self.verdict = verdict
        self.issues = issues

    def to_dict(self) -> Dict[str, Any]:
        return {
            "budget": "PASS" if self.budget_pass else "FAIL",
            "weather": "PASS" if self.weather_pass else "FAIL",
            "travel_time": "PASS" if self.travel_pass else "FAIL",
            "preference_match": "PASS" if self.preference_pass else "FAIL",
            "verdict": self.verdict,
            "issues": self.issues,
            "details": self.details,
        }


class CriticAgent:
    """Evaluates itinerary viability across all operational dimensions."""

    def __init__(self):
        self.name = "CRITIC_AGENT"

    def evaluate_itinerary(
        self,
        state: TripState,
        active_disruptions: List[DisruptionEvent],
        total_transit_mins: int = 0,
    ) -> CriticResult:
        """
        Executes holistic evaluation of the itinerary.
        """
        agent_logger.log(self.name, "Evaluating itinerary integrity across all operational dimensions")
        issues = []

        # 1. Budget Evaluation
        budget_audit = budget_agent.audit_budget(state)
        budget_pass = budget_audit["remaining"] >= 0
        if not budget_pass:
            issues.append(f"Budget exceeded by ₹{abs(budget_audit['remaining']):,.0f}.")

        # 2. Weather Evaluation
        unresolved_weather = [
            d for d in active_disruptions
            if "WEATHER" in d.event_type and d.status == "DETECTED"
        ]
        weather_pass = len(unresolved_weather) == 0
        if not weather_pass:
            for d in unresolved_weather:
                issues.append(d.description)

        # 3. Venue Closures
        unresolved_venues = [
            d for d in active_disruptions
            if "VENUE" in d.event_type and d.status == "DETECTED"
        ]
        if unresolved_venues:
            for d in unresolved_venues:
                issues.append(d.description)

        # 4. Travel Time Evaluation (e.g. > 180 mins total transit per day is excessive)
        travel_pass = total_transit_mins <= (state.goal.duration_days * 180)
        if not travel_pass:
            issues.append(f"Cumulative travel time ({total_transit_mins} mins) is excessively high.")

        # 5. Preference Match
        all_categories = [a.category.lower() for a in state.itinerary.all_activities if a.status != "REPLACED"]
        user_prefs = [p.lower() for p in state.goal.preferences]
        matches = [p for p in user_prefs if any(p in c for c in all_categories)]
        preference_pass = len(matches) > 0 or len(user_prefs) == 0
        if not preference_pass:
            issues.append("Itinerary lacks representation of specified user preferences.")

        overall_pass = budget_pass and weather_pass and travel_pass and preference_pass and (len(unresolved_venues) == 0)
        verdict = "PASS" if overall_pass else "REPLAN_REQUIRED"

        result = CriticResult(
            budget_pass=budget_pass,
            weather_pass=weather_pass,
            travel_pass=travel_pass,
            preference_pass=preference_pass,
            details={
                "budget_utilization": f"{budget_audit['utilization_pct']}%",
                "active_disruptions_count": len(active_disruptions),
                "total_transit_mins": total_transit_mins,
                "preference_matches": matches,
            },
            verdict=verdict,
            issues=issues,
        )

        agent_logger.log(
            self.name,
            f"CRITIC RESULT -> Budget: {'PASS' if budget_pass else 'FAIL'} | "
            f"Weather: {'PASS' if weather_pass else 'FAIL'} | "
            f"Travel Time: {'PASS' if travel_pass else 'FAIL'} | "
            f"Preference Match: {'PASS' if preference_pass else 'FAIL'} | "
            f"Verdict: {verdict}",
            level="WARNING" if verdict == "REPLAN_REQUIRED" else "INFO",
        )

        return result


critic_agent = CriticAgent()
