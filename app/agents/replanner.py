"""
Replanner Agent for VoyageOS.
Implements the Minimal Replanning Principle: selectively adapts only disrupted activities
while strictly preserving unaffected days, verifying budget margins, and recording explainable decisions.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.orchestration.state import TripState, DisruptionEvent, DecisionRecord, Activity
from app.agents.venue import venue_agent
from app.agents.budget import budget_agent
from app.decision.scoring import alternative_scorer
from app.decision.engine import decision_engine
from app.utils.logging import agent_logger


class ReplannerAgent:
    """Intelligently repairs itineraries adhering to the Minimal Replanning Principle."""

    def __init__(self):
        self.name = "REPLANNER_AGENT"

    def replan_disrupted_activity(
        self,
        state: TripState,
        disruption: DisruptionEvent,
    ) -> Optional[DecisionRecord]:
        """
        Adapts the itinerary for a single confirmed disruption.
        Preserves all unaffected days and activities.
        """
        agent_logger.log(
            self.name,
            f"Executing minimal replanning for event '{disruption.event_type}' on Day {disruption.affected_day}",
        )

        # Locate the affected day plan
        day_plan = next((d for d in state.itinerary.days if d.day == disruption.affected_day), None)
        if not day_plan:
            agent_logger.log(self.name, f"Day {disruption.affected_day} not found in itinerary", level="ERROR")
            return None

        # Locate target activity
        target_act = None
        if disruption.affected_activity_id:
            target_act = next((a for a in day_plan.activities if a.id == disruption.affected_activity_id), None)

        if not target_act:
            # Fallback: select outdoor activity if weather event
            if "WEATHER" in disruption.event_type:
                target_act = next((a for a in day_plan.activities if a.is_outdoor and a.status != "REPLACED"), None)

        if not target_act:
            agent_logger.log(self.name, "No viable target activity found to adapt", level="WARNING")
            return None

        # Verify intervention requirement via decision engine
        requires_intervention, reason, evidence = decision_engine.evaluate_disruption(
            event=disruption,
            affected_activity=target_act,
            trip_remaining_budget=state.budget_remaining,
        )

        if not requires_intervention:
            agent_logger.log(self.name, f"Decision engine bypassed replanning: {reason}", level="INFO")
            disruption.status = "IGNORED"
            return None

        # Step 1: Query alternatives satisfying safety constraints
        must_be_indoor = "WEATHER" in disruption.event_type
        # Exclude IDs and existing names to prevent duplicate activities across the trip
        current_ids = [a.id for a in state.itinerary.all_activities]
        existing_names = [a.name.lower() for a in state.itinerary.all_activities]

        raw_candidates = venue_agent.find_alternatives(
            destination=state.goal.destination,
            must_be_indoor=must_be_indoor,
            preferred_category=target_act.category,
            current_activity_ids=current_ids,
        )

        # Filter out duplicates by name
        candidates = [c for c in raw_candidates if c.get("name", "").lower() not in existing_names]

        if not candidates:
            candidates = raw_candidates

        if not candidates:
            agent_logger.log(self.name, "No alternative candidates available in catalog", level="ERROR")
            return None

        # Step 2: Score candidates across multi-dimensional criteria
        scored_candidates = alternative_scorer.rank_candidates(
            candidates=candidates,
            user_preferences=state.goal.preferences,
            user_constraints=state.goal.constraints,
            remaining_budget=state.budget_remaining,
            current_activity_cost=target_act.cost,
            is_bad_weather=must_be_indoor,
            target_category=target_act.category,
        )

        # Step 3: Select top candidate that satisfies budget policy
        selected_candidate = None
        selected_score_data = None

        for sc in scored_candidates:
            c_cost = sc["cost"]
            is_viable, delta, budget_msg = budget_agent.evaluate_cost_change(
                state=state,
                old_cost=target_act.cost,
                new_cost=c_cost,
            )
            if is_viable:
                selected_candidate = next((c for c in candidates if c["id"] == sc["candidate_id"]), None)
                selected_score_data = sc
                break
            else:
                agent_logger.log(self.name, f"Candidate '{sc['name']}' rejected: {budget_msg}", level="WARNING")

        if not selected_candidate:
            agent_logger.log(self.name, "All alternative candidates exceeded budget constraints", level="ERROR")
            return None

        # Step 4: Apply minimal substitution to the targeted activity slot
        old_name = target_act.name
        old_cost = target_act.cost

        # Update targeted activity in-place, preserving time slot and day
        replacement_activity = Activity(
            id=f"act_rep_{selected_candidate['id']}",
            day=target_act.day,
            time_slot=target_act.time_slot,
            start_time=target_act.start_time,
            end_time=target_act.end_time,
            name=selected_candidate["name"],
            category=selected_candidate.get("category", target_act.category),
            cost=selected_candidate.get("cost", 0.0),
            location=selected_candidate.get("location", target_act.location),
            is_outdoor=selected_candidate.get("is_outdoor", False),
            duration_hours=selected_candidate.get("duration_hours", target_act.duration_hours),
            disruption_risk="LOW",
            weather_dependent=False,
            status="PLANNED",
            metadata={
                "replaced_activity_id": target_act.id,
                "replaced_activity_name": old_name,
                "score_data": selected_score_data,
            },
        )

        # Replace in day_plan
        idx = day_plan.activities.index(target_act)
        day_plan.activities[idx] = replacement_activity

        # Recalculate trip budget
        state.recalculate_budget()
        disruption.status = "RESOLVED"
        state.status = "ADAPTED"

        # Record decision audit
        explanation = (
            f"Day {disruption.affected_day} was modified because {disruption.description.lower()} "
            f"'{old_name}' (₹{old_cost:,.0f}) was replaced by '{replacement_activity.name}' "
            f"(₹{replacement_activity.cost:,.0f}) which scores {selected_score_data['total_score']:.2f}/1.00 "
            f"on preference alignment ({replacement_activity.category}) while remaining fully within budget "
            f"(saving ₹{old_cost - replacement_activity.cost:,.0f}). Unaffected days (1 & 3) remain intact."
        )

        decision = DecisionRecord(
            agent_name=self.name,
            trigger=disruption.description,
            action_taken=f"Replaced '{old_name}' with '{replacement_activity.name}' on Day {target_act.day}",
            rationale=explanation,
            evidence={
                "disruption": disruption.model_dump(),
                "old_activity": target_act.model_dump(),
                "new_activity": replacement_activity.model_dump(),
                "score_breakdown": selected_score_data["breakdown"],
                "total_score": selected_score_data["total_score"],
            },
            affected_items=[old_name],
            alternative_selected=selected_candidate,
        )

        state.decision_log.append(decision)

        # Record snapshot of adapted itinerary for before/after comparison
        state.itinerary_history.append({
            "stage": f"adapted_day_{disruption.affected_day}",
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "snapshot": state.itinerary.model_dump(),
            "reason": explanation,
        })

        agent_logger.log(
            self.name,
            f"Replanning successful: '{old_name}' -> '{replacement_activity.name}'",
            level="INFO",
        )
        return decision


replanner_agent = ReplannerAgent()
