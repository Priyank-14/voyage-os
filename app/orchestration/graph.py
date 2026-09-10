"""
Stateful workflow graph definition for VoyageOS.
Formalizes the agentic state transitions:
Goal -> Planning -> Audit -> Critic -> Monitoring -> Decision -> Replanning -> Outcome
"""
from enum import Enum
from typing import Dict, Any, Callable, List
from app.orchestration.state import TripState
from app.utils.logging import agent_logger


class WorkflowNode(str, Enum):
    INITIAL = "INITIAL"
    PLANNING = "PLANNING"
    MOBILITY_AUDIT = "MOBILITY_AUDIT"
    CRITIC_EVALUATION = "CRITIC_EVALUATION"
    MONITORING = "MONITORING"
    DECISION_POLICY = "DECISION_POLICY"
    REPLANNING = "REPLANNING"
    ADAPTED = "ADAPTED"
    STABLE = "STABLE"


class WorkflowGraph:
    """Graph coordinator tracking execution stages and state transitions."""

    def __init__(self):
        self.current_stage = WorkflowNode.INITIAL
        self._history: List[Dict[str, Any]] = []

    def transition_to(self, target_node: WorkflowNode, metadata: Dict[str, Any] = None):
        agent_logger.log(
            "WORKFLOW_GRAPH",
            f"State Transition: {self.current_stage.value} -> {target_node.value}",
        )
        self._history.append({
            "from": self.current_stage.value,
            "to": target_node.value,
            "metadata": metadata or {},
        })
        self.current_stage = target_node

    def get_history(self) -> List[Dict[str, Any]]:
        return list(self._history)
