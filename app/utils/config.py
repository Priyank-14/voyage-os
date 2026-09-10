"""
Configuration management for VoyageOS.
Supports loading from .env, environment variables, and deterministic defaults.
"""
import os
import json
from pathlib import Path
from typing import Dict
from dotenv import load_dotenv

# Load .env if present
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    def __init__(self):
        self.APP_NAME: str = "VoyageOS"
        self.VERSION: str = "0.1.0"
        self.ENV: str = os.getenv("VOYAGEOS_ENV", "development")
        self.DEBUG: bool = os.getenv("VOYAGEOS_DEBUG", "true").lower() == "true"
        self.LOG_LEVEL: str = os.getenv("VOYAGEOS_LOG_LEVEL", "INFO")

        # Provider configuration (mock / gemini / openai)
        self.MODEL_PROVIDER: str = os.getenv("VOYAGEOS_MODEL_PROVIDER", "mock").lower()
        self.GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
        self.OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

        # External APIs (Optional)
        self.OPENWEATHER_API_KEY: str = os.getenv("OPENWEATHER_API_KEY", "")
        self.GOOGLE_MAPS_API_KEY: str = os.getenv("GOOGLE_MAPS_API_KEY", "")

        # Database
        self.DATABASE_PATH: str = os.getenv("DATABASE_PATH", str(BASE_DIR / "data" / "voyageos.db"))

        # Simulation and Thresholds
        self.SIMULATION_MODE: bool = os.getenv("SIMULATION_MODE", "true").lower() == "true"
        self.RAIN_DISRUPTION_THRESHOLD_PERCENT: float = float(
            os.getenv("RAIN_DISRUPTION_THRESHOLD_PERCENT", "70.0")
        )
        self.BUDGET_WARNING_THRESHOLD_PERCENT: float = float(
            os.getenv("BUDGET_WARNING_THRESHOLD_PERCENT", "85.0")
        )

        # Alternative Ranking Weights
        default_weights = {
            "preference": 0.30,
            "constraint": 0.25,
            "budget": 0.20,
            "travel": 0.15,
            "safety": 0.10,
        }
        weights_env = os.getenv("DEFAULT_ALTERNATIVE_SCORE_WEIGHTS")
        if weights_env:
            try:
                self.SCORE_WEIGHTS: Dict[str, float] = json.loads(weights_env)
            except Exception:
                self.SCORE_WEIGHTS = default_weights
        else:
            self.SCORE_WEIGHTS = default_weights


settings = Settings()
