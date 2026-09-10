# VoyageOS: 3–5 Minute Hackathon Demonstration Script

**Hackathon:** Tech Zephyr 4.0 — Agentic AI Hackathon (IIT Bhubaneswar)  
**Track:** Stage 1 Online Submission & Live Stage Defense  
**Target Duration:** 3 Minutes 45 Seconds  

---

## Visual Setup & Prerequisites
1. Open terminal with `.venv` active.
2. Launch Streamlit Dashboard:
   ```powershell
   streamlit run app/ui/dashboard.py
   ```
3. Have terminal split alongside browser to observe real-time agent telemetry stream.

---

## Demonstration Timeline

### 0:00 – 0:35 | Introduction & Problem Positioning
- **Spoken Narration:**
  > "Hello judges! We are presenting **VoyageOS: an Autonomous Travel Planning, Monitoring, and Re-Planning Agent**.
  >
  > Most AI travel apps today are just glorified chatbots. You ask for an itinerary, they give you static text, and their job is done. But anyone who has ever traveled knows that **the real world changes after the plan is created**. It rains, mountain passes get blocked, venues close, or budgets spiral.
  >
  > Today, when that happens, the traveler has to manually research, calculate travel times, check budgets, and rebuild their plan. **Most travel apps plan your trip. VoyageOS manages it.**"

---

### 0:35 – 1:15 | The Initial Goal & Autonomous Orchestration
- **Action on Screen:**
  - Point to the default trip parameters in the sidebar:
    - Destination: **Rishikesh**
    - Duration: **3 Days**
    - Budget: **₹15,000**
    - Preferences: **Adventure & Food**
  - Show the **Live Agent Fleet** cards in the dashboard:
    - Monitoring Agent (Active)
    - Weather Agent (Synced)
    - Mobility Agent (Routing Clear)
    - Budget Agent (₹6,150 planned / ₹15,000 ceiling)
    - Critic Agent (All PASS)
- **Spoken Narration:**
  > "Notice our initial state. VoyageOS didn't just dump text. The Goal Interpreter parsed structured constraints. The Planner generated a 3-day itinerary.
  >
  > The Mobility Agent verified travel times between Tapovan, Shivpuri, and Triveni Ghat.
  > And our Critic Agent evaluated all 5 dimensions—budget, weather safety, travel feasibility, venue hours, and preference match. Everything is green, and Day 2 features our marquee outdoor adventure: **River Rafting at Shivpuri**."

---

### 1:15 – 2:10 | The Real World Changes: Disruption Injection & Autonomous Adaptation
- **Action on Screen:**
  - Click the sidebar button: **🌧️ Inject Heavy Rain on Day 2 (85%)**.
  - Show the toast alert and the updated **Active Environmental Events** banner.
  - Navigate to **Tab 3: Before vs After (Delta)**.
- **Spoken Narration:**
  > "Now, watch what happens when the real world intervenes. We inject a severe meteorological change: **Heavy monsoon rain (85% probability) on Day 2**.
  >
  > Look at what VoyageOS does automatically:
  > 1. The **Monitoring Agent** detects the weather anomaly.
  > 2. The **Deterministic Decision Engine** checks Policy #1: Rain probability over 70% on an outdoor activity triggers mandatory intervention. River Rafting is flagged as high-risk.
  > 3. The **Replanner Agent** springs into action.
  >
  > Crucially, look at our **Minimal Replanning Principle**:
  > **Day 1 is completely untouched.**
  > **Day 3 is completely untouched.**
  > On Day 2, only the morning river rafting activity is replaced!
  > It autonomously selected **Indoor Rock Climbing & Bouldering Zone** at ₹900, preserving the traveler's adventure preference, keeping them 100% sheltered indoors, and saving ₹600 on the budget!"

---

### 2:10 – 2:50 | Transparent Multi-Criteria Scoring & Decision Audit Trail
- **Action on Screen:**
  - Click **Tab 2: Autonomous Decision Log**.
  - Expand the decision card and open **View Multi-Criteria Scoring Evidence**.
  - Highlight the exact formula components: Preference Match (1.00), Constraint Satisfaction (1.00), Budget Fit (0.97), Travel Efficiency (0.95), Safety (1.00).
- **Spoken Narration:**
  > "VoyageOS never makes 'black-box' or hallucinated decisions.
  > In our Autonomous Decision Log, every single action is audited with exact timestamps, agent provenance, trigger rationale, and transparent multi-criteria scoring.
  > You can see exactly how the scoring engine ranked candidate alternatives across preference match, constraint satisfaction, budget fit, travel efficiency, and weather safety."

---

### 2:50 – 3:20 | What-If Simulation Sandbox
- **Action on Screen:**
  - Click **Tab 4: What-If Simulator**.
  - Select Day 1, choose 'Heavy Mountain Rain & Landslide Warning', and click **Run What-If Simulation**.
  - Show the side-by-side simulation comparison report without changing the active trip.
- **Spoken Narration:**
  > "VoyageOS also provides a **What-If Simulation Sandbox**. A traveler can ask: 'What if it rains on Day 1?'
  > The system deep-copies the state, runs hypothetical perception and replanning cycles in a sandbox, and reports the exact financial and schedule delta—without mutating the traveler's active live itinerary."

---

### 3:20 – 3:45 | Tool Failure Resilience & Conclusion
- **Action on Screen:**
  - Click sidebar button: **Simulate Weather API Failure & Recovery**.
  - Show terminal and UI log indicating: `Primary service unavailable -> Activating resilient fallback engine -> Recovered via certified fallback`.
- **Spoken Narration:**
  > "Finally, VoyageOS is built for real-world resilience. If an external API like OpenWeatherMap times out, our circuit breaker retries with exponential backoff and fails over to certified local simulation models without crashing the system.
  >
  > VoyageOS is stateful, deterministic, minimal in its adaptations, and transparent in its reasoning.
  > Thank you, and we look forward to answering your questions in the technical defense!"
