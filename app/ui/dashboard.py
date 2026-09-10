"""
VoyageOS — Autonomous Travel Planning & Re-Planning Agent
Interactive Streamlit Dashboard.
"""
import streamlit as st
import json
from app.orchestration.state import TripGoal, TripState, DisruptionEvent
from app.orchestration.orchestrator import orchestrator
from app.agents.mobility import mobility_agent
from app.agents.weather import weather_agent
from app.tools.weather import weather_tool
from app.database.database import db
from app.utils.logging import agent_logger
from app.ui.components import (
    inject_custom_css,
    render_agent_status_grid,
    render_budget_metrics,
    render_before_after_diff,
)

st.set_page_config(
    page_title="VoyageOS — Autonomous Travel Agent",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_custom_css()

# Session State Initialization
if "current_trip" not in st.session_state:
    # Initialize with default Rishikesh demo trip
    demo_goal = TripGoal(
        destination="Rishikesh",
        duration_days=3,
        budget=15000.0,
        preferences=["adventure", "food"],
    )
    st.session_state.current_trip = orchestrator.create_trip(demo_goal)

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1544735716-392fe2489ffa?w=800&auto=format&fit=crop&q=60", use_container_width=True)
    st.markdown("## 🧭 VoyageOS Controls")
    st.caption("Tech Zephyr 4.0 — Agentic AI Hackathon")

    with st.expander("✨ Plan a New Trip", expanded=False):
        dest_input = st.text_input("Destination", value="Rishikesh")
        days_input = st.number_input("Duration (Days)", min_value=1, max_value=7, value=3)
        budget_input = st.number_input("Budget (₹ INR)", min_value=3000, max_value=200000, value=15000, step=1000)
        prefs_selected = st.multiselect(
            "Travel Preferences",
            options=["adventure", "food", "wellness", "culture", "sightseeing"],
            default=["adventure", "food"],
        )

        if st.button("🚀 Generate Autonomous Plan", use_container_width=True):
            new_goal = TripGoal(
                destination=dest_input,
                duration_days=int(days_input),
                budget=float(budget_input),
                preferences=prefs_selected,
            )
            st.session_state.current_trip = orchestrator.create_trip(new_goal)
            st.success(f"Trip to {dest_input} planned successfully!")
            st.rerun()

    st.markdown("---")
    st.markdown("### ⚡ Live Disruption Injection")
    st.caption("Simulate real-world conditions to observe autonomous evaluation and replanning.")

    # Disruption Trigger 1: Heavy Rain on Day 2
    if st.button("🌧️ Inject Heavy Rain on Day 2 (85%)", use_container_width=True):
        rain_event = DisruptionEvent(
            event_type="WEATHER_RAIN",
            severity="HIGH",
            affected_day=2,
            description="Heavy precipitation alert (85%) and thunderstorm advisory on Day 2.",
            probability=0.85,
            status="DETECTED",
        )
        orchestrator.handle_disruption(st.session_state.current_trip, rain_event)
        st.toast("Heavy Rain on Day 2 injected! VoyageOS triggered replanning.", icon="🌧️")
        st.rerun()

    # Disruption Trigger 2: Venue Closure
    if st.button("🚫 Inject Venue Closure (Beatles Ashram)", use_container_width=True):
        venue_event = DisruptionEvent(
            event_type="VENUE_CLOSED",
            severity="HIGH",
            affected_day=1,
            affected_activity_id="act_d1_3",
            description="The Beatles Ashram is temporarily closed for ecological restoration.",
            probability=1.0,
            status="DETECTED",
        )
        orchestrator.handle_disruption(st.session_state.current_trip, venue_event)
        st.toast("Venue closure injected! VoyageOS adapted Day 1.", icon="🚫")
        st.rerun()

    # Disruption Trigger 3: Tool Failure Recovery Simulation
    if st.button("🔄 Simulate Weather API Failure & Recovery", use_container_width=True):
        res = weather_tool.get_destination_forecast(
            destination=st.session_state.current_trip.goal.destination,
            force_failure=True,
        )
        st.toast(f"Weather API Timeout simulated! Recovered via: {res.source}", icon="🛡️")
        st.rerun()

    if st.button("🔄 Reset to Default Demo", use_container_width=True):
        demo_goal = TripGoal(
            destination="Rishikesh",
            duration_days=3,
            budget=15000.0,
            preferences=["adventure", "food"],
        )
        st.session_state.current_trip = orchestrator.create_trip(demo_goal)
        agent_logger.clear()
        st.rerun()

# ----------------- MAIN VIEW -----------------
current_trip: TripState = st.session_state.current_trip

st.markdown('<div class="main-header">VoyageOS</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Autonomous Travel Planning, Continuous Monitoring & Minimal Re-Planning System</div>', unsafe_allow_html=True)

# Top Bar Summary
col_a, col_b, col_c, col_d = st.columns(4)
col_a.metric("Destination", current_trip.goal.destination)
col_b.metric("Duration", f"{current_trip.goal.duration_days} Days")
col_c.metric("System Status", current_trip.status)
col_d.metric("Decisions Executed", len(current_trip.decision_log))

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📍 Live Trip Operations",
    "🤖 Autonomous Decision Log",
    "🔄 Before vs After (Delta)",
    "🧪 What-If Simulator",
    "📊 Observability & System Stream",
])

# ----------------- TAB 1: OPERATIONS -----------------
with tab1:
    render_agent_status_grid()
    st.markdown("---")

    render_budget_metrics(
        budget_total=current_trip.budget_total,
        budget_used=current_trip.budget_used,
        budget_remaining=current_trip.budget_remaining,
    )
    st.markdown("---")

    # Active alerts
    active_alerts = [d for d in current_trip.active_disruptions if d.status in ["DETECTED", "RESOLVED"]]
    if active_alerts:
        st.markdown("### ⚠️ Active Environmental Events")
        for alert in active_alerts:
            status_icon = "🟢 Resolved" if alert.status == "RESOLVED" else "🔴 Active Threat"
            alert_color = "success" if alert.status == "RESOLVED" else "warning"
            st.warning(f"**[{alert.event_type}] Day {alert.affected_day} ({status_icon})**: {alert.description}")

    st.markdown("### 📅 Day-by-Day Master Itinerary")
    for day in current_trip.itinerary.days:
        with st.container():
            st.markdown(f"#### 🗓️ Day {day.day} (Projected Day Spend: ₹{day.day_cost:,.0f})")
            cols = st.columns(len(day.activities)) if day.activities else [st.container()]
            for idx, act in enumerate(day.activities):
                with cols[idx % len(cols)]:
                    is_rep = "rep" in act.id
                    outdoor_text = "🌲 Outdoor" if act.is_outdoor else "🏢 Indoor"
                    card_title = f"{'🟢' if is_rep else '📌'} {act.time_slot} ({act.start_time})"
                    with st.expander(card_title, expanded=True):
                        st.markdown(f"**{act.name}**")
                        st.caption(f"📍 {act.location or 'Local'} | ⏱️ {act.duration_hours} hrs")
                        st.markdown(f"**Cost:** ₹{act.cost:,.0f}")
                        st.markdown(f"**Type:** `{act.category.upper()}` | *{outdoor_text}*")
                        if is_rep:
                            st.success("✨ Autonomously adapted alternative")

# ----------------- TAB 2: DECISION LOG -----------------
with tab2:
    st.markdown("### 📜 Autonomous Decision Audit Trail")
    st.markdown(
        "Every decision in VoyageOS is deterministically audited with timestamp, agent provenance, "
        "trigger rationale, and multi-criteria alternative scoring."
    )

    if not current_trip.decision_log:
        st.info("No autonomous replanning interventions triggered yet. Trigger a disruption in the sidebar!")
    else:
        for dec in reversed(current_trip.decision_log):
            with st.container():
                st.markdown(f"""
                <div class="decision-item">
                    <strong>⏱️ {dec.timestamp} | {dec.agent_name}</strong><br>
                    <strong>Action:</strong> {dec.action_taken}<br>
                    <strong>Trigger:</strong> {dec.trigger}<br>
                    <p style="margin-top: 0.5rem;">{dec.rationale}</p>
                </div>
                """, unsafe_allow_html=True)
                with st.expander("🔍 View Multi-Criteria Scoring Evidence"):
                    st.json(dec.evidence)

# ----------------- TAB 3: BEFORE VS AFTER -----------------
with tab3:
    render_before_after_diff(current_trip.itinerary_history)

# ----------------- TAB 4: WHAT-IF SIMULATOR -----------------
with tab4:
    st.markdown("### 🧪 What-If Scenario Sandbox")
    st.markdown("Simulate hypothetical disruptions **without modifying** your active live trip.")

    sc_col1, sc_col2 = st.columns(2)
    with sc_col1:
        sim_day = st.selectbox("Hypothetical Day", options=[1, 2, 3], index=1)
        sim_event = st.selectbox(
            "Hypothetical Disruption",
            options=[
                "Heavy Mountain Rain & Landslide Warning",
                "Road Closure / 2-Hour Transit Delay",
                "Activity Fully Booked / Closed",
            ],
        )
    with sc_col2:
        sim_prob = st.slider("Disruption Probability", min_value=0.5, max_value=1.0, value=0.9, step=0.05)

    if st.button("🚀 Run What-If Simulation", use_container_width=True):
        hypo = DisruptionEvent(
            event_type="WEATHER_RAIN" if "Rain" in sim_event else "VENUE_CLOSED",
            severity="HIGH",
            affected_day=sim_day,
            description=f"What-If Simulation: {sim_event} on Day {sim_day}",
            probability=sim_prob,
        )
        report = orchestrator.run_what_if_simulation(current_trip, hypo)

        st.success("✅ What-If Simulation Complete! Active itinerary remains unchanged.")
        res_c1, res_c2, res_c3 = st.columns(3)
        res_c1.metric("Current Plan Cost", f"₹{report['original_plan_cost']:,.0f}")
        res_c2.metric("Simulated Plan Cost", f"₹{report['simulated_plan_cost']:,.0f}")
        res_c3.metric("Projected Delta", f"₹{report['cost_difference']:,.0f}")

        st.markdown(f"**Autonomous Recommendation:** {report['recommendation']}")

# ----------------- TAB 5: OBSERVABILITY -----------------
with tab5:
    st.markdown("### 📡 Real-Time Agent Stream & Log Telemetry")
    events = agent_logger.get_events()
    if not events:
        st.info("No system events recorded in current session.")
    else:
        log_text = "\n".join([f"{e['timestamp']} [{e['agent']}] {e['message']}" for e in events])
        st.text_area("Agent Activity Logs", value=log_text, height=450)
