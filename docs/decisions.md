# Architectural Decision Records (ADRs)

This document records the foundational engineering and architectural decisions made during the development of VoyageOS.

---

## ADR-001: Minimal Replanning Principle vs. Full Itinerary Regeneration

### Status
Accepted

### Context
When real-world conditions disrupt an itinerary, naive LLM implementations prompt the model to "generate a new 3-day itinerary". This introduces major issues:
1. Traveler disorientation: activities on days that were completely unaffected are arbitrarily reshuffled or replaced.
2. Unnecessary logistical overhead: already-booked hotels, transport tickets, or reservations are discarded.
3. High computational cost and non-deterministic variations.

### Decision
VoyageOS enforces the **Minimal Replanning Principle**:
- When a disruption affects an activity on Day $k$, all other days $D \setminus \{k\}$ and unaffected activities on Day $k$ are strictly frozen.
- Only the specific disrupted slot is targeted for alternative search and replacement.

### Consequences
**Positive:** Guarantees stability, preserves traveler intention, minimizes churn, and makes adaptations transparent.  
**Negative:** Requires strict state tracking and indexing of individual activity nodes.

---

## ADR-002: Deterministic Hard Constraints Alongside LLM Reasoning

### Status
Accepted

### Context
LLMs are proficient at semantic parsing, contextual explanations, and creative recommendations, but prone to hallucinations, arithmetic errors, and unpredictable threshold adherence when evaluating numerical constraints (such as strict budget ceilings or safety probabilities).

### Decision
VoyageOS decouples decision-making into two cooperating layers:
1. **Deterministic Decision Engine:** Hard constraints (e.g., $P_{\text{rain}} \ge 70\%$ for outdoor activities; replacement cost $\le$ available funds) are encoded in deterministic Python rules.
2. **LLM Reasoning & Semantic Ranking:** The LLM interprets nuanced user preferences and synthesizes conversational explanations of decisions.

### Consequences
**Positive:** 100% reproducible decisions, eliminates budget hallucinations, and ensures safety policies cannot be bypassed.  
**Negative:** Requires maintaining explicit policy classes alongside prompt templates.

---

## ADR-003: Resilient Tool Adapters with Certified Fallbacks

### Status
Accepted

### Context
External APIs (OpenWeatherMap, Google Maps, OpenStreetMap) can suffer network timeouts, rate-limiting (429), or authentication failures during live hackathon demonstrations. Crashing the application due to an external network drop is unacceptable.

### Decision
Implement `execute_with_resilience` wrapping all external tools:
1. Primary API call executed with retry attempts and exponential backoff.
2. If primary fails or is forced to fail (for demonstration), system gracefully shifts to certified local fallback providers.
3. Every response tags its provenance (`source="primary"` vs `source="fallback"`).

### Consequences
**Positive:** 100% demo reliability, graceful degradation, and full transparency on data origin.  
**Negative:** Requires maintaining realistic local baseline data profiles for demo destinations.

---

## ADR-004: Explicit Structured State with SQLite Persistence

### Status
Accepted

### Context
Conversational chatbots maintain state solely inside context windows, leading to token exhaustion, context forgetting, and loss of historical snapshots when sessions refresh.

### Decision
VoyageOS maintains state through explicit Pydantic models (`TripState`, `Activity`, `DayPlan`, `DisruptionEvent`, `DecisionRecord`) backed by a persistent SQLite database with thread-safe serialization.

### Consequences
**Positive:** Full state reproducibility, offline auditing, zero context window bloat, and fast recovery across app reboots.

---

## ADR-005: Grand Finale Domain Independence

### Status
Accepted

### Context
Tech Zephyr 4.0 Stage 2 (Grand Finale) releases a completely new, surprise problem statement requiring the team to build a working prototype in 24 hours.

### Decision
The core agentic workflow graph:
$$\text{State} \longrightarrow \text{Planner} \longrightarrow \text{Sensors} \longrightarrow \text{Critic} \longrightarrow \text{Decision Engine} \longrightarrow \text{Replanner} \longrightarrow \text{Outcome}$$
is designed to be strictly domain-independent. Replacing `WeatherAgent` and `PlacesTool` with `SensorTelemetryAgent` and `ResourceCatalog` allows repurposing the core engine for disaster logistics, warehouse replenishment, or server workload balancing within 2 hours.
