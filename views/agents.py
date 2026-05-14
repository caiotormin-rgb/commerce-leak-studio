import streamlit as st

from shared import CONSULTANCY_NAME

AGENTS = [
    {
        "name": "Chargeback Triage",
        "color": "#ff5566",
        "opportunity": "R$420k",
        "opportunity_sub": "at-risk orders caught per year",
        "watches": ["🚨 Risk", "🏷️ Categories"],
        "problem": "Suspicious orders ship before anyone notices. By the time a dispute arrives, the product is gone and the reversal fee is yours. Most merchants only see the pattern after losing three or four months of margin.",
        "solution": "Runs every Monday at 02:00. Compares chargeback flag rates across all categories week-over-week. Any category with a rising flag rate gets a payment hold drafted and sellers flagged for pre-shipment review — automatically.",
        "impact": "Bad orders stopped before they leave the warehouse. Finance gets a ticket. Ops has flagged sellers in their queue before the day starts. No analyst time required.",
        "screenshot": """
<div style="background:#08080f;border:1px solid #1c1c2a;border-radius:8px;padding:20px 24px;font-family:'JetBrains Mono',monospace;font-size:12px;line-height:1.7">
  <div style="color:#ff5566;font-size:10px;letter-spacing:.12em;text-transform:uppercase;margin-bottom:12px">◆ CHARGEBACK TRIAGE · Mon 02:00 UTC · 3 categories flagged</div>
  <div style="color:#eeeeff;margin-bottom:4px">── Period delta: Aug → Sep ───────────────────────────</div>
  <div style="color:#ff5566">▲ Computers Accessories   +2.4pp  →  7.1% flag rate   ALERT</div>
  <div style="color:#ff8a4c">▲ Office Furniture        +1.1pp  →  5.5%</div>
  <div style="color:#f5c542">▲ Telephony               +0.8pp  →  4.9%</div>
  <div style="color:#6060a0">  Watches Gifts           −0.2pp  →  3.1%   ok</div>
  <div style="margin:16px 0 4px;color:#eeeeff">── Actions taken ─────────────────────────────────────</div>
  <div style="color:#22d3a0">✓  [INTERNAL TICKET → Finance] Hold payment release · Computers Accessories · ref #CHB-0291</div>
  <div style="color:#22d3a0">✓  [EMAIL TO DEPT → ops@luma.co] Flag top 3 sellers for pre-shipment review</div>
  <div style="color:#f5c542">○  [INTERNAL TICKET → Finance] Watch queue · Office Furniture · evidence required</div>
  <div style="margin:16px 0 0;color:#3a3a6a">Completed 4.2s · next run Mon 02:00</div>
</div>
""",
    },
    {
        "name": "Repeat Customer Detector",
        "color": "#f5c542",
        "opportunity": "R$38k+",
        "opportunity_sub": "in lost repeat purchases · per bad month",
        "watches": ["🔄 Retention", "🚚 Fulfillment"],
        "problem": "When customers stop coming back, you don't feel it for months. By then the cohort is gone, the root cause is buried, and there's nothing left to recover. The problem is usually fulfillment — not the product.",
        "solution": "Runs monthly. Detects cohort return-rate drops, cross-references them against delivery performance and review scores to determine cause. Surfaces the finding before the next cohort is affected.",
        "impact": "You know within 30 days which month went wrong and why. Customers who experienced that bad month get a targeted recovery email with a gift card before the silence becomes permanent.",
        "screenshot": """
<div style="background:#08080f;border:1px solid #1c1c2a;border-radius:8px;padding:20px 24px;font-family:'JetBrains Mono',monospace;font-size:12px;line-height:1.7">
  <div style="color:#f5c542;font-size:10px;letter-spacing:.12em;text-transform:uppercase;margin-bottom:12px">◆ REPEAT CUSTOMER DETECTOR · monthly run · anomaly found</div>
  <div style="color:#eeeeff;margin-bottom:4px">── Cohort return rates ───────────────────────────────</div>
  <div style="color:#6060a0">  Jun 2017   180d return   3.8%   normal</div>
  <div style="color:#6060a0">  Jul 2017   180d return   4.1%   normal</div>
  <div style="color:#ff5566">▲ Aug 2017   180d return   1.9%   SHARP DROP  ← root cause below</div>
  <div style="color:#6060a0">  Sep 2017   180d return   3.7%   normal</div>
  <div style="margin:16px 0 4px;color:#eeeeff">── What happened in Aug 2017? ────────────────────────</div>
  <div style="color:#f5c542">  On-time rate     81.3%   ← lowest in 12 months</div>
  <div style="color:#f5c542">  Avg review score   3.6   ← vs 4.1 in normal months</div>
  <div style="color:#22d3a0">→ Cause: fulfillment delays. 717 customers did not return.</div>
  <div style="color:#22d3a0">→ Estimated missed revenue: R$38k over 180 days.</div>
  <div style="margin:16px 0 4px;color:#eeeeff">── Actions taken ─────────────────────────────────────</div>
  <div style="color:#22d3a0">✓  [ISSUE GIFT CARD → 717 customers] R$15 voucher · subject: "We owe you a better experience"</div>
  <div style="color:#22d3a0">✓  [EMAIL TO DEPT → ops@luma.co] Delivery SLA review requested · Aug 2017 cohort</div>
  <div style="margin:16px 0 0;color:#3a3a6a">Completed 6.8s · 1 anomaly flagged · 717 customers queued</div>
</div>
""",
    },
    {
        "name": "Budget Reallocation Advisor",
        "color": "#7c6bff",
        "opportunity": "R$22k",
        "opportunity_sub": "projected LTV uplift · per planning cycle",
        "watches": ["🎯 Attribution", "🏷️ Categories", "🔄 Retention"],
        "problem": "Every quarter someone builds a spreadsheet and guesses where to put the budget. The guess ignores fraud exposure, delivery performance, and which categories actually produce repeat buyers. Capital goes to the wrong places.",
        "solution": "Runs quarterly. Scores every category across review quality, on-time delivery, chargeback risk, and 180-day LTV. Produces a ranked reallocation table with estimated revenue impact per shift.",
        "impact": "A ranked decision replaces days of analyst prep. Finance and Growth get a ticket with the recommended split and the modeled upside — ready to debate, not research.",
        "screenshot": """
<div style="background:#08080f;border:1px solid #1c1c2a;border-radius:8px;padding:20px 24px;font-family:'JetBrains Mono',monospace;font-size:12px;line-height:1.7">
  <div style="color:#7c6bff;font-size:10px;letter-spacing:.12em;text-transform:uppercase;margin-bottom:12px">◆ BUDGET REALLOCATION · Q4 · R$480k total · 4 signals</div>
  <div style="color:#6060a0;margin-bottom:12px">signals: review score · on-time rate · chargeback risk · 180d LTV</div>
  <div style="color:#eeeeff;margin-bottom:6px">── Ranked recommendation ─────────────────────────────</div>
  <div style="color:#22d3a0">▲ INCREASE  Auto            health 84   +R$62k   low risk · high LTV</div>
  <div style="color:#22d3a0">▲ INCREASE  Health Beauty   health 79   +R$44k   strong repeat</div>
  <div style="color:#22d3a0">▲ INCREASE  Watches Gifts   health 76   +R$28k   high AOV · low fraud</div>
  <div style="color:#6060a0">  HOLD      Bed Bath Table  health 61   ±R$0     stable</div>
  <div style="color:#f5c542">▼ REDUCE    Office Furn.    health 41   −R$18k   chargebacks rising</div>
  <div style="color:#ff5566">▼ REDUCE    Computers       health 28   −R$40k   7.1% fraud · low score</div>
  <div style="color:#22d3a0;margin-top:12px">→ Net projected LTV uplift: +R$22k over 180 days.</div>
  <div style="margin:16px 0 4px;color:#eeeeff">── Actions taken ─────────────────────────────────────</div>
  <div style="color:#22d3a0">✓  [INTERNAL TICKET → Growth] Q4 budget split · ranked table attached · ready to review</div>
  <div style="color:#22d3a0">✓  [EMAIL TO DEPT → finance@luma.co] Reallocation model · sign-off requested by Fri</div>
  <div style="margin:16px 0 0;color:#3a3a6a">Completed 3.1s · ready for review</div>
</div>
""",
    },
    {
        "name": "Seller Health Monitor",
        "color": "#22d3a0",
        "opportunity": "R$197k",
        "opportunity_sub": "in seller revenue · protected per year",
        "watches": ["🏪 Sellers", "🚚 Fulfillment"],
        "problem": "Seller performance slips gradually — a few more late deliveries, a few more bad reviews. Nobody notices until customers are already complaining in public. By then the seller may need to be removed, and that revenue disappears with them.",
        "solution": "Runs nightly across all sellers. Any seller breaching delivery or review SLA thresholds gets flagged, classified by severity, and has a warning notice drafted automatically — ready to send at 08:00.",
        "impact": "Problems are caught in hours, not weeks. The email to the seller is already written. Ops has a queue to action before the team's first meeting.",
        "screenshot": """
<div style="background:#08080f;border:1px solid #1c1c2a;border-radius:8px;padding:20px 24px;font-family:'JetBrains Mono',monospace;font-size:12px;line-height:1.7">
  <div style="color:#22d3a0;font-size:10px;letter-spacing:.12em;text-transform:uppercase;margin-bottom:12px">◆ SELLER HEALTH MONITOR · nightly · 3,095 sellers checked</div>
  <div style="color:#eeeeff;margin-bottom:4px">── Threshold breaches ────────────────────────────────</div>
  <div style="color:#ff5566">▲ CRITICAL  4a3ca931  Bed Bath Table  on_time 74%  score 3.4  ← both</div>
  <div style="color:#ff8a4c">▲ WARN      d1bfe1c2  Furniture       on_time 81%  score 3.8</div>
  <div style="color:#f5c542">▲ WATCH     9f7b55a4  Telephony       score 3.6    on_time ok</div>
  <div style="margin:16px 0 4px;color:#eeeeff">── Notice drafted: seller 4a3ca931 ───────────────────</div>
  <div style="color:#6060a0">"On-time rate 74% — below 80% SLA floor. Review score 3.4.</div>
  <div style="color:#6060a0"> Submit improvement plan within 7 days or listings suppressed."</div>
  <div style="margin:16px 0 4px;color:#eeeeff">── Actions taken ─────────────────────────────────────</div>
  <div style="color:#22d3a0">✓  [SEND AUTO EMAIL → seller 4a3ca931] SLA breach notice · 7-day cure window</div>
  <div style="color:#22d3a0">✓  [EMAIL TO DEPT → ops@luma.co] 3 alerts queued · 1 critical · action required today</div>
  <div style="color:#f5c542">○  [INTERNAL TICKET → Marketplace Ops] Watch: d1bfe1c2 · review next cycle</div>
  <div style="margin:16px 0 0;color:#3a3a6a">Completed 2.9s · 3 alerts · 1 critical · sent 08:00</div>
</div>
""",
    },
    {
        "name": "Review Crisis Responder",
        "color": "#ff8a4c",
        "opportunity": "R$85k",
        "opportunity_sub": "in at-risk revenue · per bad-review wave",
        "watches": ["🏷️ Categories", "🚚 Fulfillment"],
        "problem": "A 1-star spike goes unnoticed for days while more reviews accumulate. By the time someone flags it in a meeting, the damage to the category's ranking and repeat rate is already done — and it was usually a delivery problem, not a product defect.",
        "solution": "Monitors review score distributions daily. On a spike event, traces whether the cause is delivery lateness or product quality, then generates a specific recovery plan for that category.",
        "impact": "From spike to action plan in under 10 minutes. Affected customers get an outreach email the same day. Ops gets an escalation. The right team gets the right task — not a general alert.",
        "screenshot": """
<div style="background:#08080f;border:1px solid #1c1c2a;border-radius:8px;padding:20px 24px;font-family:'JetBrains Mono',monospace;font-size:12px;line-height:1.7">
  <div style="color:#ff8a4c;font-size:10px;letter-spacing:.12em;text-transform:uppercase;margin-bottom:12px">◆ REVIEW CRISIS RESPONDER · triggered 09:14 UTC</div>
  <div style="color:#ff5566;margin-bottom:12px">EVENT: 1-star spike · Furniture Decor · +8.3pp this month</div>
  <div style="color:#eeeeff;margin-bottom:4px">── Causal trace ──────────────────────────────────────</div>
  <div style="color:#f5c542">  Orders 8–14 days late   avg score 1.67   ↑ volume spike</div>
  <div style="color:#6060a0">  On-time orders          avg score 4.29   stable</div>
  <div style="color:#22d3a0;margin-top:8px">→ Root cause: fulfillment delays. Not product quality.</div>
  <div style="color:#22d3a0">→ 312 affected orders in window. Action before more reviews post.</div>
  <div style="margin:16px 0 4px;color:#eeeeff">── Actions taken ─────────────────────────────────────</div>
  <div style="color:#22d3a0">✓  [SEND AUTO EMAIL → 312 customers] "We know your order was late — here's what we're doing"</div>
  <div style="color:#22d3a0">✓  [ISSUE GIFT CARD → 312 customers] R$20 voucher · attached to outreach email</div>
  <div style="color:#22d3a0">✓  [EMAIL TO DEPT → ops@luma.co] SLA review: Furniture Decor · logistics escalation</div>
  <div style="color:#f5c542">○  [INTERNAL TICKET → CX] Monitor: check for public replies to outreach · 48h window</div>
  <div style="margin:16px 0 0;color:#3a3a6a">Completed 5.1s · time to first action: &lt;10 minutes</div>
</div>
""",
    },
    {
        "name": "Geo Expansion Scout",
        "color": "#38bdf8",
        "opportunity": "R$210k",
        "opportunity_sub": "annual revenue · top underserved state",
        "watches": ["🚚 Fulfillment", "🏷️ Categories"],
        "problem": "Some states have thousands of customers ordering but almost no local sellers to fulfil them. Packages travel further, arrive later, reviews fall, and those customers don't return. The gap is invisible until someone maps order density against seller density.",
        "solution": "Runs quarterly. Scores every state by orders-per-seller ratio and on-time rate. For the top gaps, drafts a seller recruitment brief with delivery time estimates and revenue projections — ready to send to the partnerships team.",
        "impact": "A map problem becomes a hiring list. The partnerships team gets a ticket with state-by-state briefs, ranked by opportunity size. No research required.",
        "screenshot": """
<div style="background:#08080f;border:1px solid #1c1c2a;border-radius:8px;padding:20px 24px;font-family:'JetBrains Mono',monospace;font-size:12px;line-height:1.7">
  <div style="color:#38bdf8;font-size:10px;letter-spacing:.12em;text-transform:uppercase;margin-bottom:12px">◆ GEO EXPANSION SCOUT · Q4 · seller recruitment · 26 states scored</div>
  <div style="color:#eeeeff;margin-bottom:4px">── Opportunity ranking ───────────────────────────────</div>
  <div style="color:#22d3a0">▲  1  BA (Bahia)     3,392 orders   7 sellers   on_time 79%   TOP GAP</div>
  <div style="color:#22d3a0">▲  2  MG (Minas G.)  7,013 orders  34 sellers   on_time 85%</div>
  <div style="color:#f5c542">○  3  RS (R.G.Sul)   4,880 orders  22 sellers   on_time 83%</div>
  <div style="color:#6060a0">   4  PR (Paraná)    4,175 orders  31 sellers   on_time 88%   saturating</div>
  <div style="margin:16px 0 4px;color:#eeeeff">── Brief: Bahia ──────────────────────────────────────</div>
  <div style="color:#6060a0">3,392 orders / 7 sellers. Avg delivery 24 days vs 12d in SP.</div>
  <div style="color:#22d3a0">→ 4–6 new sellers in Salvador → −3.2 day delivery improvement.</div>
  <div style="color:#22d3a0">→ Revenue opportunity: R$180k–R$240k at current demand.</div>
  <div style="margin:16px 0 4px;color:#eeeeff">── Actions taken ─────────────────────────────────────</div>
  <div style="color:#22d3a0">✓  [INTERNAL TICKET → Partnerships] Seller recruitment · BA, MG, RS · briefs attached</div>
  <div style="color:#22d3a0">✓  [EMAIL TO DEPT → partnerships@luma.co] Q4 expansion targets · 3 markets · ranked</div>
  <div style="margin:16px 0 0;color:#3a3a6a">Completed 4.7s · 3 market briefs generated · ticket #GEO-0047</div>
</div>
""",
    },
    {
        "name": "Manufacturer Escalation",
        "color": "#9b72cf",
        "opportunity": "R$130k",
        "opportunity_sub": "in quality-driven churn · per affected category",
        "watches": ["🏷️ Categories", "🔄 Retention"],
        "problem": "1-star reviews caused by genuine product defects never reach the manufacturer. They get misread as delivery problems, no one escalates upstream, and defective units keep shipping. By the time someone investigates, the category has hundreds of bad reviews and a damaged repeat rate.",
        "solution": "Runs weekly. Separates quality-driven reviews from delivery-driven ones by cross-referencing review scores against delivery timing — on-time orders with 1-star reviews are product signals. When a category exceeds the quality-spike threshold, drafts a formal escalation to the manufacturer with 30 days of evidence.",
        "impact": "The manufacturer receives a structured brief before more defective stock ships. The category team decides whether to pause listings or require a quality audit. The problem stops compounding at the source.",
        "screenshot": """
<div style="background:#08080f;border:1px solid #1c1c2a;border-radius:8px;padding:20px 24px;font-family:'JetBrains Mono',monospace;font-size:12px;line-height:1.7">
  <div style="color:#9b72cf;font-size:10px;letter-spacing:.12em;text-transform:uppercase;margin-bottom:12px">◆ MANUFACTURER ESCALATION · weekly · quality signal scan</div>
  <div style="color:#eeeeff;margin-bottom:4px">── Quality vs delivery signal split ──────────────────</div>
  <div style="color:#6060a0">  Method: on-time orders with 1★ = product signal · late orders with 1★ = delivery signal</div>
  <div style="margin:10px 0 4px;color:#eeeeff">── Categories above quality threshold ────────────────</div>
  <div style="color:#ff5566">▲ ESCALATE  Sports Leisure    quality 1★  38%   on-time 91%   PRODUCT DEFECT</div>
  <div style="color:#ff8a4c">▲ WATCH     Garden Tools      quality 1★  22%   on-time 88%</div>
  <div style="color:#6060a0">  ok        Health Beauty     quality 1★   8%   on-time 84%   normal</div>
  <div style="margin:16px 0 4px;color:#eeeeff">── Escalation brief: Sports Leisure ──────────────────</div>
  <div style="color:#6060a0">412 delivered-on-time orders · avg score 1.9 · past 30 days.</div>
  <div style="color:#6060a0">Review keywords: "broke after first use", "wrong size", "missing part".</div>
  <div style="color:#9b72cf">→ Delivery ruled out. Defect pattern consistent across sellers.</div>
  <div style="color:#9b72cf">→ Estimated churn impact: R$130k in lost 180d repeat revenue.</div>
  <div style="margin:16px 0 4px;color:#eeeeff">── Actions taken ─────────────────────────────────────</div>
  <div style="color:#22d3a0">✓  [SEND AUTO EMAIL → manufacturer contact] Formal quality escalation · 30-day evidence pack</div>
  <div style="color:#22d3a0">✓  [INTERNAL TICKET → Category Mgmt] Listing review: Sports Leisure · pause or audit?</div>
  <div style="color:#22d3a0">✓  [EMAIL TO DEPT → ops@luma.co] Pre-shipment inspection flag · Sports Leisure stock</div>
  <div style="color:#f5c542">○  [INTERNAL TICKET → CX] Draft response template for affected buyers · 48h</div>
  <div style="margin:16px 0 0;color:#3a3a6a">Completed 3.8s · 1 escalation sent · 1 category paused · ticket #MFR-0088</div>
</div>
""",
    },
]


def render():
    st.markdown(f"""
<div style="background:#101026;border:1px solid #2a2a55;border-left:4px solid #7c6bff;border-radius:10px;padding:28px 30px;margin-bottom:28px">
  <p style="font-family:monospace;font-size:10px;color:#5a5a78;letter-spacing:.12em;text-transform:uppercase;margin:0 0 10px">{CONSULTANCY_NAME} · agentic automation · built on this dataset</p>
  <h2 style="color:#eeeeff;font-size:28px;font-weight:900;margin:0 0 10px;line-height:1.15">The data already knows where the money is.<br>These agents go get it.</h2>
  <p style="color:#8d8daf;font-size:15px;line-height:1.65;margin:0 0 20px;max-width:720px">Seven automations derived directly from the leaks in this dashboard. Each one runs on a schedule, finds a specific problem, and takes a concrete action — not a report.</p>
  <div style="display:flex;gap:32px;flex-wrap:wrap;margin-bottom:20px">
    <div><p style="font-family:monospace;font-size:10px;color:#5a5a78;letter-spacing:.1em;text-transform:uppercase;margin:0 0 4px">Total opportunity modeled</p><p style="color:#eeeeff;font-size:24px;font-weight:900;margin:0">R$1.1M+</p></div>
    <div><p style="font-family:monospace;font-size:10px;color:#5a5a78;letter-spacing:.1em;text-transform:uppercase;margin:0 0 4px">Agents running</p><p style="color:#eeeeff;font-size:24px;font-weight:900;margin:0">7</p></div>
    <div><p style="font-family:monospace;font-size:10px;color:#5a5a78;letter-spacing:.1em;text-transform:uppercase;margin:0 0 4px">Analyst hours automated / week</p><p style="color:#eeeeff;font-size:24px;font-weight:900;margin:0">~14h</p></div>
  </div>
  <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center">
    <span style="font-family:monospace;font-size:10px;color:#5a5a78;letter-spacing:.1em;text-transform:uppercase">Actions each agent can take:</span>
    <span style="background:#1a1a2e;border:1px solid #2a2a44;color:#9090c0;font-family:monospace;font-size:10px;padding:3px 10px;border-radius:4px">Send auto email</span>
    <span style="background:#1a1a2e;border:1px solid #2a2a44;color:#9090c0;font-family:monospace;font-size:10px;padding:3px 10px;border-radius:4px">Email to department</span>
    <span style="background:#1a1a2e;border:1px solid #2a2a44;color:#9090c0;font-family:monospace;font-size:10px;padding:3px 10px;border-radius:4px">Create internal ticket</span>
    <span style="background:#1a1a2e;border:1px solid #2a2a44;color:#9090c0;font-family:monospace;font-size:10px;padding:3px 10px;border-radius:4px">Issue gift card</span>
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
        watches_html = "".join(
            f'<span style="background:{agent["color"]}15;color:{agent["color"]};border:1px solid {agent["color"]}44;'
            f'font-family:monospace;font-size:10px;padding:3px 10px;border-radius:4px;margin-right:6px">{w}</span>'
            for w in agent["watches"]
        )
        st.markdown(f"""
<div style="background:#0f0f18;border:1px solid #1c1c2a;border-left:4px solid {agent["color"]};border-radius:10px;padding:26px 28px">
  <p style="font-family:monospace;font-size:10px;color:#5a5a78;letter-spacing:.1em;text-transform:uppercase;margin:0 0 6px">{idx + 1} of {len(AGENTS)} · monitors</p>
  <div style="margin-bottom:18px">{watches_html}</div>

  <h2 style="color:#eeeeff;font-size:22px;font-weight:900;margin:0 0 6px;line-height:1.2">{agent["name"]}</h2>
  <div style="margin:0 0 22px">
    <span style="color:{agent["color"]};font-size:30px;font-weight:900;line-height:1">{agent["opportunity"]}</span>
    <span style="color:#5a5a78;font-size:12px;font-family:monospace;margin-left:8px">{agent["opportunity_sub"]}</span>
  </div>

  <div style="display:flex;flex-direction:column;gap:0">

    <div style="padding:16px 0;border-top:1px solid #1c1c2a">
      <p style="font-family:monospace;font-size:9px;color:{agent["color"]};letter-spacing:.14em;text-transform:uppercase;margin:0 0 7px">Problem</p>
      <p style="color:#c0c0e0;font-size:13px;line-height:1.7;margin:0">{agent["problem"]}</p>
    </div>

    <div style="padding:16px 0;border-top:1px solid #1c1c2a">
      <p style="font-family:monospace;font-size:9px;color:{agent["color"]};letter-spacing:.14em;text-transform:uppercase;margin:0 0 7px">Solution</p>
      <p style="color:#c0c0e0;font-size:13px;line-height:1.7;margin:0">{agent["solution"]}</p>
    </div>

    <div style="padding:16px 0;border-top:1px solid #1c1c2a">
      <p style="font-family:monospace;font-size:9px;color:{agent["color"]};letter-spacing:.14em;text-transform:uppercase;margin:0 0 7px">Impact</p>
      <p style="color:#c0c0e0;font-size:13px;line-height:1.7;margin:0">{agent["impact"]}</p>
    </div>

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
| **Chargeback Triage** | R$420k | Total value of all orders showing two or more dispute signals over the two-year dataset. That's the money that was at risk before any intervention. |
| **Repeat Customer Detector** | R$38k+ | Worst delivery month (Aug 2017): 717 customers compared against what similar customers spent in normal months over the following 180 days. The gap is what was lost. |
| **Budget Reallocation Advisor** | R$22k | Projected LTV difference when budget shifts toward health-scored categories versus the current mix, applied to a R$480k quarterly envelope. |
| **Seller Health Monitor** | R$197k | Annual revenue of the single highest-earning seller currently below acceptable delivery and review thresholds — what's at risk if the seller deteriorates further or exits. |
| **Review Crisis Responder** | R$85k | Late-arriving orders in the affected category during a spike month, multiplied by average order value. The revenue pool where customers are most likely to churn. |
| **Geo Expansion Scout** | R$210k | Bahia: 3,392 orders, 7 local sellers, avg delivery 24 days. Revenue at current demand plus a conservative uplift for improved delivery speed. |
| **Manufacturer Escalation** | R$130k | On-time orders with 1-star reviews in Sports Leisure over a 30-day window, multiplied by the average 180-day repeat spend difference between satisfied and dissatisfied customers. |

These are illustrations of the size of the problem each agent is designed to catch — not a promise of what you'll recover.
""")
        st.markdown('<p class="kpi-label" style="margin-top:8px">Based on: 2 years of Olist Brazil orders · payments · reviews · delivery records</p>', unsafe_allow_html=True)
