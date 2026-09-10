"""
Central Orchestrator for VoyageOS.
Coordinates specialized agents, coordinates conditional execution graph,
manages persistence, and executes What-If simulations.
"""
from typing import Dict, Any, Optional, List
import copy
from app.orchestration.state import TripGoal, TripState, DisruptionEvent, DecisionRecord
from app.orchestration.graph import WorkflowGraph, WorkflowNode
from app.agents.planner import planner_agent
from app.agents.weather import weather_agent
from app.agents.mobility import mobility_agent
from app.agents.venue import venue_agent
from app.agents.budget import budget_agent
from app.agents.critic import critic_agent
from app.agents.monitor import monitoring_agent
from app.agents.replanner import replanner_agent
from app.database.database import db
from app.utils.logging import agent_logger


class Orchestrator:
    """Master controller managing the agentic loop."""

    def __init__(self):
        self.name = "ORCHESTRATOR"

    def create_trip(self, goal: TripGoal) -> TripState:
        """
        Executes initial planning workflow:
        Goal -> Planner -> Mobility Audit -> Critic -> Save DB
        """
        graph = WorkflowGraph()
        agent_logger.log(self.name, f"Starting trip generation for {goal.destination} ({goal.duration_days} days)")

        # 1. Planning stage
        graph.transition_to(WorkflowNode.PLANNING)
        state = planner_agent.plan_trip(goal)

        # 2. Mobility transit evaluation
        graph.transition_to(WorkflowNode.MOBILITY_AUDIT)
        transit_audit = mobility_agent.audit_itinerary_transit(state)

        # 3. Critic verification
        graph.transition_to(WorkflowNode.CRITIC_EVALUATION)
        critic_res = critic_agent.evaluate_itinerary(
            state=state,
            active_disruptions=[],
            total_transit_mins=transit_audit["total_transit_mins"],
        )

        state.status = "MONITORING"
        graph.transition_to(WorkflowNode.STABLE)

        # Persist to database
        db.save_trip(state)
        agent_logger.log(self.name, f"Trip {state.trip_id} initialized and stored in SQLite database")
        return state

    def handle_disruption(self, state: TripState, disruption: DisruptionEvent) -> TripState:
        """
        Processes a disruption event through the agentic loop:
        Disruption -> Decision Policy -> Replanner (if needed) -> Critic -> Save DB
        """
        graph = WorkflowGraph()
        agent_logger.log(self.name, f"Orchestrator received disruption: {disruption.event_type} on Day {disruption.affected_day}")

        state.active_disruptions.append(disruption)
        graph.transition_to(WorkflowNode.DECISION_POLICY)

        # Trigger minimal replanner
        graph.transition_to(WorkflowNode.REPLANNING)
        decision = replanner_agent.replan_disrupted_activity(state, disruption)

        # Re-evaluate with critic post-adaptation
        graph.transition_to(WorkflowNode.CRITIC_EVALUATION)
        transit_audit = mobility_agent.audit_itinerary_transit(state)
        critic_res = critic_agent.evaluate_itinerary(
            state=state,
            active_disruptions=[d for d in state.active_disruptions if d.status == "DETECTED"],
            total_transit_mins=transit_audit["total_transit_mins"],
        )

        graph.transition_to(WorkflowNode.ADAPTED)
        db.save_trip(state)
        agent_logger.log(self.name, f"Trip {state.trip_id} successfully updated with decision record")
        return state

    def run_monitoring_scan(
        self,
        state: TripState,
        simulated_weather_day: Optional[int] = None,
        simulated_weather_prob: float = 0.85,
        simulated_closed_venue_id: Optional[str] = None,
        simulated_traffic_day: Optional[int] = None,
        force_weather_failure: bool = False,
    ) -> TripState:
        """
        Executes an autonomous monitoring cycle.
        If any disruptions are detected, routes them to handle_disruption.
        """
        agent_logger.log(self.name, f"Initiating scheduled environmental scan for trip {state.trip_id}")
        detected = monitoring_agent.scan_environment(
            state=state,
            simulated_weather_day=simulated_weather_day,
            simulated_weather_prob=simulated_weather_prob,
            simulated_closed_venue_id=simulated_closed_venue_id,
            simulated_traffic_day=simulated_traffic_day,
            force_weather_failure=force_weather_failure,
        )

        for event in detected:
            self.handle_disruption(state, event)

        return state

    def run_what_if_simulation(
        self,
        current_state: TripState,
        hypothetical_disruption: DisruptionEvent,
    ) -> Dict[str, Any]:
        """
        Runs a What-If simulation without modifying the active trip state.
        Returns a side-by-side comparison report.
        """
        agent_logger.log(
            self.name,
            f"Running What-If simulation: '{hypothetical_disruption.description}' on Day {hypothetical_disruption.affected_day}",
        )

        # Deep copy state so active trip is strictly preserved
        simulated_state = copy.deepcopy(current_state)

        # Apply replanning in sandbox
        decision = replanner_agent.replan_disrupted_activity(simulated_state, hypothetical_disruption)

        # Compare metrics
        orig_cost = current_state.budget_used
        sim_cost = simulated_state.budget_used
        delta_cost = sim_cost - orig_cost

        return {
            "scenario": hypothetical_disruption.description,
            "affected_day": hypothetical_disruption.affected_day,
            "decision_record": decision.model_dump() if decision else None,
            "original_plan_cost": orig_cost,
            "simulated_plan_cost": sim_cost,
            "cost_difference": delta_cost,
            "original_itinerary": current_state.itinerary.model_dump(),
            "simulated_itinerary": simulated_state.itinerary.model_dump(),
            "recommendation": (
                decision.rationale if decision
                else "No modification required; current plan satisfies constraints under simulated scenario."
            ),
        }


orchestrator = Orchestrator()
