import streamlit as st

from shared import CONSULTANCY_NAME

AGENTS = [
    {
        "name": "Chargeback Triage",
        "color": "#ff5566",
        "opportunity": "R$420k",
        "opportunity_sub": "in suspicious orders · spotted each year",
        "pitch": "Every week, some product categories quietly attract more fraudulent or disputed orders than others — and no one notices until the money is already gone. This agent checks every Monday morning and acts before anything ships.",
        "recovers": "Stops bad orders before they leave the warehouse. No more end-of-month surprises.",
        "screenshot": """
<div style="background:#08080f;border:1px solid #1c1c2a;border-radius:8px;padding:20px 24px;font-family:'JetBrains Mono',monospace;font-size:12px;line-height:1.7">
  <div style="color:#ff5566;font-size:10px;letter-spacing:.12em;text-transform:uppercase;margin-bottom:12px">◆ CHARGEBACK TRIAGE · Mon 02:00 UTC</div>
  <div style="color:#eeeeff;margin-bottom:4px">── Period delta: Aug → Sep ───────────────────────────</div>
  <div style="color:#ff5566">▲ Computers Accessories   +2.4pp  →  7.1% flag rate   ALERT</div>
  <div style="color:#ff8a4c">▲ Office Furniture        +1.1pp  →  5.5%</div>
  <div style="color:#f5c542">▲ Telephony               +0.8pp  →  4.9%</div>
  <div style="color:#6060a0">  Watches Gifts           −0.2pp  →  3.1%   ok</div>
  <div style="margin:16px 0 4px;color:#eeeeff">── Actions drafted ───────────────────────────────────</div>
  <div style="color:#22d3a0">✓  Hold payment release — Computers Accessories</div>
  <div style="color:#22d3a0">✓  Flag top 3 sellers for pre-shipment review</div>
  <div style="color:#f5c542">○  Require evidence capture — Office Furniture</div>
  <div style="margin:16px 0 0;color:#6060a0">→ Brief sent to finance@luma.co · ops@luma.co</div>
  <div style="margin-top:12px;color:#3a3a6a">Completed 4.2s · next run Mon 02:00</div>
</div>
""",
    },
    {
        "name": "Repeat Customer Detector",
        "color": "#f5c542",
        "opportunity": "R$38k+",
        "opportunity_sub": "in lost repeat purchases · per bad month",
        "pitch": "When customers stop coming back, you don't feel it for months. By then the damage is done. This agent spots the early warning signs each month and tells you exactly what went wrong — a bad delivery run, a dip in reviews — while you can still do something about it.",
        "recovers": "Catches the problem while there's still time to fix it. Explains the cause, not just the symptom.",
        "screenshot": """
<div style="background:#08080f;border:1px solid #1c1c2a;border-radius:8px;padding:20px 24px;font-family:'JetBrains Mono',monospace;font-size:12px;line-height:1.7">
  <div style="color:#f5c542;font-size:10px;letter-spacing:.12em;text-transform:uppercase;margin-bottom:12px">◆ REPEAT CUSTOMER DETECTOR · monthly run</div>
  <div style="color:#eeeeff;margin-bottom:4px">── How many customers came back? ─────────────────────</div>
  <div style="color:#6060a0">  Jun 2017   return rate  normal</div>
  <div style="color:#6060a0">  Jul 2017   return rate  normal</div>
  <div style="color:#ff5566">▲ Aug 2017   return rate  SHARP DROP  ← investigate</div>
  <div style="color:#6060a0">  Sep 2017   return rate  normal</div>
  <div style="margin:16px 0 4px;color:#eeeeff">── What happened in Aug 2017? ────────────────────────</div>
  <div style="color:#f5c542">  On-time deliveries  81.3%   ← lowest in the past year</div>
  <div style="color:#f5c542">  Customer ratings     3.6    ← vs 4.1 in normal months</div>
  <div style="margin:16px 0 4px;color:#eeeeff">── Conclusion ────────────────────────────────────────</div>
  <div style="color:#22d3a0">→ Deliveries ran late in August. Ratings fell.</div>
  <div style="color:#22d3a0">  717 customers didn't come back as a result.</div>
  <div style="color:#22d3a0">→ Estimated value of those lost repeat purchases: R$38k.</div>
  <div style="margin-top:12px;color:#3a3a6a">Completed 6.8s · 1 anomaly flagged</div>
</div>
""",
    },
    {
        "name": "Budget Reallocation Advisor",
        "color": "#7c6bff",
        "opportunity": "R$22k",
        "opportunity_sub": "in extra revenue · per planning cycle",
        "pitch": "Every quarter, someone builds a spreadsheet and guesses where to put the budget. This agent looks at customer reviews, delivery performance, fraud exposure, and repeat purchase rates all at once — and tells you exactly which categories to double down on and which to pull back from.",
        "recovers": "Replaces days of analyst prep. Finds the shift no one had time to model.",
        "screenshot": """
<div style="background:#08080f;border:1px solid #1c1c2a;border-radius:8px;padding:20px 24px;font-family:'JetBrains Mono',monospace;font-size:12px;line-height:1.7">
  <div style="color:#7c6bff;font-size:10px;letter-spacing:.12em;text-transform:uppercase;margin-bottom:12px">◆ BUDGET REALLOCATION · Q4 · R$480k total</div>
  <div style="color:#6060a0;margin-bottom:16px">signals: review score · on-time rate · chargeback risk · ltv 180d</div>
  <div style="color:#eeeeff;margin-bottom:8px">── Ranked recommendation ─────────────────────────────</div>
  <div style="color:#22d3a0">▲ INCREASE  Auto            score 84   +R$62k   low risk · high LTV</div>
  <div style="color:#22d3a0">▲ INCREASE  Health Beauty   score 79   +R$44k   strong repeat</div>
  <div style="color:#22d3a0">▲ INCREASE  Watches Gifts   score 76   +R$28k   high AOV · low fraud</div>
  <div style="color:#6060a0">  HOLD      Bed Bath Table  score 61   ±R$0     stable</div>
  <div style="color:#f5c542">▼ REDUCE    Office Furn.    score 41   −R$18k   chargebacks rising</div>
  <div style="color:#ff5566">▼ REDUCE    Computers       score 28   −R$40k   7.1% fraud · low score</div>
  <div style="margin:16px 0 0;color:#22d3a0">→ Net: +R$22k projected LTV uplift over 180 days.</div>
  <div style="margin-top:12px;color:#3a3a6a">Completed 3.1s · ready for review</div>
</div>
""",
    },
    {
        "name": "Seller Health Monitor",
        "color": "#22d3a0",
        "opportunity": "R$197k",
        "opportunity_sub": "in seller revenue · caught before it walks out the door",
        "pitch": "When a seller starts slipping — late deliveries, falling ratings — it happens slowly enough that nobody notices until customers are already complaining. This agent checks all 3,000+ sellers every night and has a warning email drafted before your team gets to work.",
        "recovers": "Problems get flagged in hours, not weeks. The email is already written.",
        "screenshot": """
<div style="background:#08080f;border:1px solid #1c1c2a;border-radius:8px;padding:20px 24px;font-family:'JetBrains Mono',monospace;font-size:12px;line-height:1.7">
  <div style="color:#22d3a0;font-size:10px;letter-spacing:.12em;text-transform:uppercase;margin-bottom:12px">◆ SELLER HEALTH MONITOR · nightly · 3,095 sellers</div>
  <div style="color:#eeeeff;margin-bottom:4px">── Breaches flagged ──────────────────────────────────</div>
  <div style="color:#ff5566">▲ ALERT   4a3ca931  Bed Bath Table  on_time 74%  score 3.4  ← both</div>
  <div style="color:#ff8a4c">▲ WARN    d1bfe1c2  Furniture       on_time 81%  score 3.8</div>
  <div style="color:#f5c542">▲ WATCH   9f7b55a4  Telephony       score 3.6    on_time ok</div>
  <div style="margin:16px 0 4px;color:#eeeeff">── Alert drafted for 4a3ca931 ────────────────────────</div>
  <div style="color:#6060a0">"Your on-time rate dropped to 74% — below the 80% SLA floor.</div>
  <div style="color:#6060a0"> Review score is 3.4. Submit an improvement plan within 7 days</div>
  <div style="color:#6060a0"> or listings will be suppressed."</div>
  <div style="margin:16px 0 0;color:#6060a0">→ Queued for ops@luma.co · severity: critical</div>
  <div style="margin-top:12px;color:#3a3a6a">Completed 2.9s · 3 alerts queued · 1 critical</div>
</div>
""",
    },
    {
        "name": "Review Crisis Responder",
        "color": "#ff8a4c",
        "opportunity": "R$85k",
        "opportunity_sub": "in at-risk revenue · per bad-review wave",
        "pitch": "When 1-star reviews suddenly spike for a product category, it usually means something went wrong with deliveries — not the product itself. This agent catches the spike the moment it happens, figures out the cause, and has a response plan ready before the team even starts their day.",
        "recovers": "From spike to action plan in minutes. Customer outreach starts before more damage accumulates.",
        "screenshot": """
<div style="background:#08080f;border:1px solid #1c1c2a;border-radius:8px;padding:20px 24px;font-family:'JetBrains Mono',monospace;font-size:12px;line-height:1.7">
  <div style="color:#ff8a4c;font-size:10px;letter-spacing:.12em;text-transform:uppercase;margin-bottom:12px">◆ REVIEW CRISIS RESPONDER · triggered 09:14 UTC</div>
  <div style="color:#ff5566;margin-bottom:12px">EVENT: 1-star spike — Furniture Decor · +8.3pp this month</div>
  <div style="color:#eeeeff;margin-bottom:4px">── Causal trace ──────────────────────────────────────</div>
  <div style="color:#f5c542">  Orders 8–14 days late   avg score 1.67   ↑ volume</div>
  <div style="color:#6060a0">  On-time orders          avg score 4.29   stable</div>
  <div style="margin:16px 0 4px;color:#eeeeff">── Recovery plan ─────────────────────────────────────</div>
  <div style="color:#22d3a0">→ Root cause: fulfillment delays. Not product quality.</div>
  <div style="color:#22d3a0">→ Ops: open SLA review with logistics this week.</div>
  <div style="color:#22d3a0">→ CX: outreach to affected orders before more reviews post.</div>
  <div style="margin:16px 0 0;color:#6060a0">→ Escalation drafted · owners notified</div>
  <div style="margin-top:12px;color:#3a3a6a">Completed 5.1s · time to action: &lt;10 minutes</div>
</div>
""",
    },
    {
        "name": "Geo Expansion Scout",
        "color": "#38bdf8",
        "opportunity": "R$210k",
        "opportunity_sub": "annual revenue · top underserved state",
        "pitch": "Some states have thousands of customers ordering but almost no local sellers to fulfil them. So packages travel further, arrive later, reviews suffer, and those customers don't come back. This agent finds those gaps and writes the seller recruitment brief for each one.",
        "recovers": "Turns a map problem into a hiring list. One market brief per state, ready to send.",
        "screenshot": """
<div style="background:#08080f;border:1px solid #1c1c2a;border-radius:8px;padding:20px 24px;font-family:'JetBrains Mono',monospace;font-size:12px;line-height:1.7">
  <div style="color:#38bdf8;font-size:10px;letter-spacing:.12em;text-transform:uppercase;margin-bottom:12px">◆ GEO EXPANSION SCOUT · Q4 seller recruitment</div>
  <div style="color:#eeeeff;margin-bottom:4px">── Opportunity ranking ───────────────────────────────</div>
  <div style="color:#22d3a0">▲  1  BA (Bahia)     3,392 orders  7 sellers   on_time 79%   TOP PICK</div>
  <div style="color:#22d3a0">▲  2  MG (Minas G.)  7,013 orders  34 sellers  on_time 85%</div>
  <div style="color:#f5c542">○  3  RS (R.G.Sul)   4,880 orders  22 sellers  on_time 83%</div>
  <div style="color:#6060a0">   4  PR (Paraná)    4,175 orders  31 sellers  on_time 88%   saturating</div>
  <div style="margin:16px 0 4px;color:#eeeeff">── Brief: Bahia ──────────────────────────────────────</div>
  <div style="color:#6060a0">3,392 orders from 7 local sellers. Avg delivery 24 days.</div>
  <div style="color:#22d3a0">→ 4–6 new sellers in Salvador → −3.2 days delivery.</div>
  <div style="color:#22d3a0">→ Revenue opportunity: R$180k–R$240k at current demand.</div>
  <div style="margin-top:12px;color:#3a3a6a">Completed 4.7s · 3 market briefs generated</div>
</div>
""",
    },
]


def render():
    st.markdown(f"""
<div style="background:#101026;border:1px solid #2a2a55;border-left:4px solid #7c6bff;border-radius:10px;padding:28px 30px;margin-bottom:28px">
  <p style="font-family:monospace;font-size:10px;color:#5a5a78;letter-spacing:.12em;text-transform:uppercase;margin:0 0 10px">{CONSULTANCY_NAME} · agentic automation · built on this dataset</p>
  <h2 style="color:#eeeeff;font-size:28px;font-weight:900;margin:0 0 10px;line-height:1.15">The data already knows where the money is.<br>These agents go get it.</h2>
  <p style="color:#8d8daf;font-size:15px;line-height:1.65;margin:0 0 20px;max-width:720px">Six automations derived directly from the leaks in this dashboard. Each one runs on a schedule, finds a specific type of revenue at risk, and delivers a decision — not a report.</p>
  <div style="display:flex;gap:32px;flex-wrap:wrap">
    <div><p style="font-family:monospace;font-size:10px;color:#5a5a78;letter-spacing:.1em;text-transform:uppercase;margin:0 0 4px">Total opportunity modeled</p><p style="color:#eeeeff;font-size:24px;font-weight:900;margin:0">R$972k+</p></div>
    <div><p style="font-family:monospace;font-size:10px;color:#5a5a78;letter-spacing:.1em;text-transform:uppercase;margin:0 0 4px">Agents running</p><p style="color:#eeeeff;font-size:24px;font-weight:900;margin:0">6</p></div>
    <div><p style="font-family:monospace;font-size:10px;color:#5a5a78;letter-spacing:.1em;text-transform:uppercase;margin:0 0 4px">Analyst hours automated / week</p><p style="color:#eeeeff;font-size:24px;font-weight:900;margin:0">~12h</p></div>
  </div>
</div>
""", unsafe_allow_html=True)

    if "agent_idx" not in st.session_state:
        st.session_state.agent_idx = 0

    idx   = st.session_state.agent_idx
    agent = AGENTS[idx]

    nav_cols = st.columns([1, 6, 1])
    with nav_cols[0]:
        if st.button("← Prev", use_container_width=True, disabled=(idx == 0)):
            st.session_state.agent_idx -= 1
            st.rerun()
    with nav_cols[1]:
        pill_html = "".join(
            f'<span style="display:inline-block;padding:4px 14px;border-radius:999px;font-size:11px;font-family:monospace;margin:0 3px;'
            f'background:{"#1a1a28" if i != idx else a["color"] + "22"};'
            f'color:{"#eeeeff" if i == idx else "#5a5a78"};'
            f'border:1px solid {a["color"] + "55" if i == idx else "#2a2a40"}">'
            f'{a["name"].split()[0]}</span>'
            for i, a in enumerate(AGENTS)
        )
        st.markdown(f'<div style="text-align:center;padding:8px 0">{pill_html}</div>', unsafe_allow_html=True)
    with nav_cols[2]:
        if st.button("Next →", use_container_width=True, disabled=(idx == len(AGENTS) - 1)):
            st.session_state.agent_idx += 1
            st.rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown(f"""
<div style="background:#0f0f18;border:1px solid #1c1c2a;border-left:4px solid {agent["color"]};border-radius:10px;padding:26px 28px">
  <p style="font-family:monospace;font-size:10px;color:#5a5a78;letter-spacing:.1em;text-transform:uppercase;margin:0 0 14px">{idx + 1} of {len(AGENTS)}</p>
  <h2 style="color:#eeeeff;font-size:24px;font-weight:900;margin:0 0 4px;line-height:1.2">{agent["name"]}</h2>
  <div style="margin:0 0 20px">
    <span style="color:{agent["color"]};font-size:32px;font-weight:900;line-height:1">{agent["opportunity"]}</span>
    <span style="color:#5a5a78;font-size:12px;font-family:monospace;margin-left:8px">{agent["opportunity_sub"]}</span>
  </div>
  <p style="color:#c0c0e0;font-size:14px;line-height:1.75;margin:0 0 20px">{agent["pitch"]}</p>
  <div style="background:#0a0a16;border-left:3px solid {agent["color"]}55;border-radius:0 6px 6px 0;padding:12px 16px">
    <p style="font-family:monospace;font-size:10px;color:#5a5a78;letter-spacing:.1em;text-transform:uppercase;margin:0 0 5px">What it recovers</p>
    <p style="color:#9090b8;font-size:13px;line-height:1.6;margin:0">{agent["recovers"]}</p>
  </div>
</div>
""", unsafe_allow_html=True)

    with right:
        st.markdown(f"""
<div>
  <p style="font-family:monospace;font-size:10px;color:#5a5a78;letter-spacing:.1em;text-transform:uppercase;margin:0 0 8px">Sample output</p>
  {agent["screenshot"]}
</div>
""", unsafe_allow_html=True)

    st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

    with st.expander("Where do these numbers come from?"):
        st.markdown("""
All figures come directly from the real Olist Brazil sales dataset used in this dashboard (covering about 2 years of orders).
They're conservative estimates based on what actually happened — not forecasts or assumptions.

| Agent | Estimated opportunity | How we got there |
|---|---|---|
| **Chargeback Triage** | R$420k | We added up the total value of all orders that showed two or more warning signs of fraud or dispute over the two-year period. That's the money that was at risk. |
| **Repeat Customer Detector** | R$38k+ | We found the worst month for delivery problems (August 2017) and compared how much those 717 customers spent over the following 6 months versus what customers in normal months typically spent. The gap is what was lost. |
| **Budget Reallocation Advisor** | R$22k | We compared how much repeat customers spend when budget is shifted toward well-performing categories versus the current mix. The R$22k is the difference — applied to a R$480k quarterly budget. |
| **Seller Health Monitor** | R$197k | This is the annual revenue of the single highest-earning seller currently slipping below acceptable delivery and rating thresholds. It represents what's at risk if nothing is done and that seller gets removed or stops performing. |
| **Review Crisis Responder** | R$85k | We took the number of late-arriving orders in the affected category during a spike month and multiplied by the average order value. That's the revenue pool where customers are most likely to leave bad reviews and not come back. |
| **Geo Expansion Scout** | R$210k | Bahia had 3,392 orders but only 7 local sellers, causing much longer delivery times. We multiplied the order volume by the average order value and added a modest uplift for the improvement in customer experience that faster delivery would bring. |

These are illustrations of the size of the problem each agent is designed to catch — not a promise of what you'll recover.
How much you actually get back depends on how quickly you act and how your specific operation responds.
""")
        st.markdown('<p class="kpi-label" style="margin-top:8px">Based on: 2 years of Olist Brazil orders · payments · reviews · delivery records</p>', unsafe_allow_html=True)
