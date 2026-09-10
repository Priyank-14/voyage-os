"""
Resilience and graceful failure recovery module for VoyageOS tool calls.
Handles retries, exponential backoffs, circuit fallbacks, and provenance tagging.
"""
import time
from typing import Callable, Any, Dict, Optional
from app.utils.logging import agent_logger


class ToolCallResult:
    """Standardized envelope for tool execution results."""

    def __init__(
        self,
        data: Any,
        source: str = "primary",  # "primary" | "fallback" | "simulated"
        retries_attempted: int = 0,
        status: str = "success",  # "success" | "recovered" | "failed"
        error_message: Optional[str] = None,
    ):
        self.data = data
        self.source = source
        self.retries_attempted = retries_attempted
        self.status = status
        self.error_message = error_message

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "retries_attempted": self.retries_attempted,
            "status": self.status,
            "error_message": self.error_message,
        }


def execute_with_resilience(
    primary_fn: Callable[[], Any],
    fallback_fn: Callable[[], Any],
    tool_name: str,
    max_retries: int = 2,
    base_delay_sec: float = 0.5,
    force_failure: bool = False,
) -> ToolCallResult:
    """
    Executes primary tool function with retries. If primary exhausts retries or
    force_failure is enabled (for live demo), switches seamlessly to fallback.
    """
    retries = 0

    if not force_failure:
        while retries <= max_retries:
            try:
                agent_logger.log(tool_name, f"Executing primary service (attempt {retries + 1}/{max_retries + 1})")
                data = primary_fn()
                agent_logger.log(tool_name, "Primary service call successful", level="INFO")
                return ToolCallResult(
                    data=data,
                    source="primary",
                    retries_attempted=retries,
                    status="success",
                )
            except Exception as e:
                retries += 1
                agent_logger.log(
                    tool_name,
                    f"Primary service failed: {str(e)}. Retrying...",
                    level="WARNING",
                )
                if retries <= max_retries:
                    time.sleep(base_delay_sec * (2 ** (retries - 1)))

    # Primary failed or was forced to fail for live demonstration
    agent_logger.log(
        tool_name,
        "Primary service unavailable. Activating resilient fallback engine...",
        level="WARNING",
    )
    try:
        fallback_data = fallback_fn()
        agent_logger.log(
            tool_name,
            "Recovered successfully via certified fallback provider",
            level="INFO",
        )
        return ToolCallResult(
            data=fallback_data,
            source="fallback",
            retries_attempted=retries,
            status="recovered",
            error_message="Primary service timed out; fallback recovered data.",
        )
    except Exception as fallback_err:
        agent_logger.log(
            tool_name,
            f"Both primary and fallback failed: {str(fallback_err)}",
            level="ERROR",
        )
        return ToolCallResult(
            data=None,
            source="failed",
            retries_attempted=retries,
            status="failed",
            error_message=str(fallback_err),
        )
