"""
Budget Agent for VoyageOS.
Tracks financial boundaries, projected spend, margins, and evaluates cost feasibility.
"""
from typing import Dict, Any, Tuple, Optional
from app.orchestration.state import TripState, DisruptionEvent
from app.utils.logging import agent_logger
from app.utils.config import settings


class BudgetAgent:
    """Monitors financial parameters and enforces budget limits."""

    def __init__(self):
        self.name = "BUDGET_AGENT"

    def audit_budget(self, state: TripState) -> Dict[str, Any]:
        """
        Calculates total projected spend, remaining funds, and utilization percentage.
        """
        state.recalculate_budget()
        utilization_pct = (state.budget_used / state.budget_total) * 100 if state.budget_total > 0 else 0.0

        is_critical = state.budget_remaining < 0
        is_warning = utilization_pct >= settings.BUDGET_WARNING_THRESHOLD_PERCENT and not is_critical

        status_tag = "EXCEEDED" if is_critical else ("WARNING" if is_warning else "HEALTHY")

        agent_logger.log(
            self.name,
            f"Budget Audit: Total=₹{state.budget_total:,.0f} | Used=₹{state.budget_used:,.0f} | "
            f"Remaining=₹{state.budget_remaining:,.0f} ({utilization_pct:.1f}% utilized, Status: {status_tag})",
        )

        return {
            "total": state.budget_total,
            "used": state.budget_used,
            "remaining": state.budget_remaining,
            "utilization_pct": round(utilization_pct, 1),
            "status": status_tag,
        }

    def evaluate_cost_change(
        self,
        state: TripState,
        old_cost: float,
        new_cost: float,
    ) -> Tuple[bool, float, str]:
        """
        Checks if replacing an activity with old_cost by one with new_cost violates the budget.
        Returns (is_viable, delta_cost, explanation).
        """
        delta = new_cost - old_cost
        projected_remaining = state.budget_remaining - delta

        if projected_remaining >= 0:
            msg = (
                f"Proposed replacement cost (₹{new_cost:,.0f}) is viable. "
                f"Delta: {'+' if delta >= 0 else ''}₹{delta:,.0f}. Projected remaining: ₹{projected_remaining:,.0f}."
            )
            agent_logger.log(self.name, msg, level="INFO")
            return True, delta, msg
        else:
            msg = (
                f"Proposed replacement cost (₹{new_cost:,.0f}) exceeds total budget by ₹{abs(projected_remaining):,.0f}."
            )
            agent_logger.log(self.name, msg, level="WARNING")
            return False, delta, msg


budget_agent = BudgetAgent()
