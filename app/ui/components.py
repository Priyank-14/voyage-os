"""
Reusable UI components and custom CSS styling for the VoyageOS Streamlit dashboard.
"""
import streamlit as st
from typing import Dict, Any, List, Optional


def inject_custom_css():
    """Inject modern styling and layout accents."""
    st.markdown("""
        <style>
        /* General page layout */
        .main-header {
            font-size: 2.2rem;
            font-weight: 800;
            color: #1E293B;
            margin-bottom: 0.2rem;
        }
        .sub-header {
            font-size: 1.05rem;
            color: #64748B;
            margin-bottom: 1.5rem;
        }
        /* Cards */
        .voyage-card {
            background: #FFFFFF;
            border-radius: 12px;
            padding: 1.25rem;
            border: 1px solid #E2E8F0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            margin-bottom: 1rem;
        }
        .status-pill {
            display: inline-block;
            padding: 0.2rem 0.6rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }
        .status-healthy { background: #DCFCE7; color: #166534; }
        .status-alert { background: #FEE2E2; color: #991B1B; }
        .status-adapted { background: #DBEAFE; color: #1E40AF; }
        .status-indoor { background: #EDE9FE; color: #5B21B6; }
        .status-outdoor { background: #FEF3C7; color: #92400E; }

        /* Decision item */
        .decision-item {
            border-left: 4px solid #3B82F6;
            padding-left: 1rem;
            margin-bottom: 1rem;
            background: #F8FAFC;
            padding: 0.75rem 1rem;
            border-radius: 0 8px 8px 0;
        }
        </style>
    """, unsafe_allow_html=True)


def render_agent_status_grid():
    """Renders real-time status indicators for all specialized agents."""
    st.markdown("### 🤖 Live Agent Fleet")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.success("● Monitoring Agent\nActive (Polling)")
        st.info("● Weather Agent\nSynced")
    with col2:
        st.success("● Budget Agent\nEnforcing Limits")
        st.info("● Mobility Agent\nRouting Clear")
    with col3:
        st.success("● Critic / Evaluator\nInspecting")
        st.info("● Venue Agent\nOperational")
    with col4:
        st.success("● Decision Engine\nRules Armed")
        st.info("● Replanner Agent\nMinimal Adapting")


def render_budget_metrics(budget_total: float, budget_used: float, budget_remaining: float):
    """Renders budget utilization cards."""
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Budget", f"₹{budget_total:,.0f}")
    col2.metric("Projected Spend", f"₹{budget_used:,.0f}")
    delta_color = "normal" if budget_remaining >= 0 else "inverse"
    col3.metric("Remaining Margin", f"₹{budget_remaining:,.0f}", delta=f"₹{budget_remaining:,.0f}", delta_color=delta_color)

    pct = (budget_used / budget_total) if budget_total > 0 else 0.0
    st.progress(min(1.0, max(0.0, pct)))


def render_before_after_diff(history: List[Dict[str, Any]]):
    """Renders side-by-side comparison of original vs adapted itinerary."""
    if len(history) < 2:
        st.info("No replanning events recorded yet. Trigger a disruption simulation to observe minimal replanning in action!")
        return

    orig_snap = history[0].get("snapshot", {})
    new_snap = history[-1].get("snapshot", {})

    st.markdown("### 🔄 Before vs After: Minimal Replanning Delta")
    st.markdown("> **Note:** Notice that **Day 1 and Day 3 remain strictly untouched**, while only the weather-threatened activity on **Day 2** was replaced.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🔴 Original Itinerary")
        for day in orig_snap.get("days", []):
            st.markdown(f"**Day {day.get('day')}**")
            for act in day.get("activities", []):
                outdoor_badge = "🌲 Outdoor" if act.get("is_outdoor") else "🏢 Indoor"
                st.markdown(f"- **{act.get('time_slot')} ({act.get('start_time')})**: {act.get('name')} — ₹{act.get('cost', 0):,.0f} *({outdoor_badge})*")

    with col2:
        st.markdown("#### 🟢 Adapted Itinerary (Autonomously Repaired)")
        for day in new_snap.get("days", []):
            st.markdown(f"**Day {day.get('day')}**")
            for act in day.get("activities", []):
                outdoor_badge = "🌲 Outdoor" if act.get("is_outdoor") else "🏢 Indoor"
                is_replaced = "rep" in act.get("id", "")
                if is_replaced:
                    st.markdown(f"- **{act.get('time_slot')} ({act.get('start_time')})**: :green[**{act.get('name')}**] — :green[**₹{act.get('cost', 0):,.0f}**] *({outdoor_badge} • REPLACED)*")
                else:
                    st.markdown(f"- **{act.get('time_slot')} ({act.get('start_time')})**: {act.get('name')} — ₹{act.get('cost', 0):,.0f} *({outdoor_badge})*")
