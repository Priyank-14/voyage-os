"""
Transparent multi-criteria scoring engine for evaluating itinerary alternatives.
Computes explainable weighted scores across preferences, constraints, budget, travel, and safety.
"""
from typing import Dict, Any, List, Optional
from app.utils.config import settings


class AlternativeScorer:
    """Calculates transparent, explainable rankings for candidate alternatives."""

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or settings.SCORE_WEIGHTS

    def score_candidate(
        self,
        candidate: Dict[str, Any],
        user_preferences: List[str],
        user_constraints: Dict[str, Any],
        remaining_budget: float,
        current_activity_cost: float,
        is_bad_weather: bool = False,
        target_category: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Evaluates a single alternative candidate on normalized [0.0, 1.0] dimensions.
        Returns total weighted score and component breakdowns.
        """
        cat = candidate.get("category", "").lower()
        cost = candidate.get("cost", 0.0)
        is_outdoor = candidate.get("is_outdoor", True)

        # 1. Preference Match & Category Continuity (0.0 to 1.0)
        user_prefs_lower = [p.lower() for p in user_preferences]
        if target_category and cat == target_category.lower():
            # Perfect category continuity (e.g. adventure -> indoor adventure)
            pref_score = 1.0
        elif cat in user_prefs_lower:
            pref_score = 0.90
        elif any(p in candidate.get("name", "").lower() for p in user_prefs_lower):
            pref_score = 0.80
        else:
            pref_score = 0.50

        # 2. Constraint Satisfaction (0.0 to 1.0)
        # If bad weather, an indoor activity satisfies constraint 1.0, outdoor 0.0
        constraint_score = 1.0
        if is_bad_weather and is_outdoor:
            constraint_score = 0.0
        # If user explicitly specified avoidances
        avoidances = user_constraints.get("avoidances", [])
        if any(a.lower() in cat or a.lower() in candidate.get("name", "").lower() for a in avoidances):
            constraint_score = 0.0

        # 3. Budget Fit (0.0 to 1.0)
        # Higher score if it comfortably fits budget without large overrun
        max_allowable = remaining_budget + current_activity_cost
        if max_allowable <= 0:
            budget_score = 1.0 if cost == 0 else 0.0
        elif cost > max_allowable:
            budget_score = 0.0
        else:
            # Cheaper or equal cost gets high marks; cost near limit gets proportional
            savings_ratio = (max_allowable - cost) / max_allowable
            budget_score = 0.5 + (0.5 * savings_ratio)

        # 4. Travel Efficiency (0.0 to 1.0)
        # Tapovan/central locations score higher for accessibility
        loc = candidate.get("location", "").lower()
        if "tapovan" in loc or "laxman jhula" in loc or "ram jhula" in loc:
            travel_score = 0.95
        elif "mohan chatti" in loc or "kunjapuri" in loc:
            travel_score = 0.60
        else:
            travel_score = 0.80

        # 5. Weather / Safety Suitability (0.0 to 1.0)
        if is_bad_weather:
            safety_score = 1.0 if not is_outdoor else 0.1
        else:
            safety_score = 0.95

        # Weighted total
        w_pref = self.weights.get("preference", 0.30)
        w_const = self.weights.get("constraint", 0.25)
        w_budg = self.weights.get("budget", 0.20)
        w_trav = self.weights.get("travel", 0.15)
        w_safe = self.weights.get("safety", 0.10)

        total_score = (
            (pref_score * w_pref)
            + (constraint_score * w_const)
            + (budget_score * w_budg)
            + (travel_score * w_trav)
            + (safety_score * w_safe)
        )

        return {
            "candidate_id": candidate.get("id"),
            "name": candidate.get("name"),
            "category": candidate.get("category"),
            "cost": cost,
            "is_outdoor": is_outdoor,
            "total_score": round(total_score, 3),
            "breakdown": {
                "preference_match": round(pref_score, 2),
                "constraint_satisfaction": round(constraint_score, 2),
                "budget_fit": round(budget_score, 2),
                "travel_efficiency": round(travel_score, 2),
                "weather_safety": round(safety_score, 2),
            },
        }

    def rank_candidates(
        self,
        candidates: List[Dict[str, Any]],
        user_preferences: List[str],
        user_constraints: Dict[str, Any],
        remaining_budget: float,
        current_activity_cost: float,
        is_bad_weather: bool = False,
        target_category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Scores and ranks candidates in descending order of total score."""
        scored = [
            self.score_candidate(
                c,
                user_preferences=user_preferences,
                user_constraints=user_constraints,
                remaining_budget=remaining_budget,
                current_activity_cost=current_activity_cost,
                is_bad_weather=is_bad_weather,
                target_category=target_category,
            )
            for c in candidates
        ]
        # Sort descending by total score
        scored.sort(key=lambda x: x["total_score"], reverse=True)
        return scored


alternative_scorer = AlternativeScorer()
