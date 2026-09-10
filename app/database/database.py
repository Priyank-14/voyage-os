"""
SQLite persistence layer for VoyageOS.
Provides thread-safe storage for trips, state snapshots, and audit logs.
"""
import sqlite3
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from app.orchestration.state import TripState
from app.database.models import serialize_trip_state, deserialize_trip_state
from app.utils.config import settings


class Database:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.DATABASE_PATH
        # Ensure parent directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trips (
                    trip_id TEXT PRIMARY KEY,
                    created_at TEXT,
                    destination TEXT,
                    duration_days INTEGER,
                    budget_total REAL,
                    budget_used REAL,
                    budget_remaining REAL,
                    goal_json TEXT,
                    itinerary_json TEXT,
                    disruptions_json TEXT,
                    decisions_json TEXT,
                    history_json TEXT,
                    status TEXT
                )
            """)
            conn.commit()

    def save_trip(self, state: TripState) -> None:
        data = serialize_trip_state(state)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO trips (
                    trip_id, created_at, destination, duration_days,
                    budget_total, budget_used, budget_remaining,
                    goal_json, itinerary_json, disruptions_json,
                    decisions_json, history_json, status
                ) VALUES (
                    :trip_id, :created_at, :destination, :duration_days,
                    :budget_total, :budget_used, :budget_remaining,
                    :goal_json, :itinerary_json, :disruptions_json,
                    :decisions_json, :history_json, :status
                )
                ON CONFLICT(trip_id) DO UPDATE SET
                    budget_used = :budget_used,
                    budget_remaining = :budget_remaining,
                    itinerary_json = :itinerary_json,
                    disruptions_json = :disruptions_json,
                    decisions_json = :decisions_json,
                    history_json = :history_json,
                    status = :status
            """, data)
            conn.commit()

    def get_trip(self, trip_id: str) -> Optional[TripState]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM trips WHERE trip_id = ?", (trip_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return deserialize_trip_state(dict(row))

    def list_trips(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT trip_id, created_at, destination, duration_days, budget_total, status FROM trips ORDER BY created_at DESC")
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def delete_trip(self, trip_id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM trips WHERE trip_id = ?", (trip_id,))
            conn.commit()
            return cursor.rowcount > 0


# Default global instance
db = Database()
