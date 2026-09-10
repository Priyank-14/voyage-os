"""
Observability and agent activity logging for VoyageOS.
Provides structured terminal logging and an in-memory event stream for UI dashboards.
"""
import sys
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

# Ensure UTF-8 output on Windows consoles
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Configure root logger
stream_handler = logging.StreamHandler(sys.stdout)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[stream_handler],
)


class AgentLogger:
    """Agent logger supporting observability for terminal output and UI event streams."""

    def __init__(self):
        self._events: List[Dict[str, Any]] = []
        self._raw_logger = logging.getLogger("VoyageOS")

    def log(
        self,
        agent: str,
        message: str,
        level: str = "INFO",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{agent.upper()}] {message}"

        event = {
            "timestamp": timestamp,
            "agent": agent.upper(),
            "message": message,
            "level": level.upper(),
            "metadata": metadata or {},
        }
        self._events.append(event)

        if level.upper() == "WARNING":
            self._raw_logger.warning(formatted)
        elif level.upper() == "ERROR":
            self._raw_logger.error(formatted)
        else:
            self._raw_logger.info(formatted)

    def get_events(self) -> List[Dict[str, Any]]:
        """Return all logged agent events."""
        return list(self._events)

    def clear(self):
        """Clear recorded events."""
        self._events.clear()


agent_logger = AgentLogger()
