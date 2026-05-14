import streamlit as st
from html import escape

from shared import brl, render_brief_box, DEMO_BRIEF, generate_openai_brief, RETAILER_NAME


def render(wf, total_spend, avg_mer, total_claimed, overclaim_pct,
           fl_on_time, fl_days, fl_orders_k,
           ret_repeat, ret_ltv, ret_customers_k,
           action_queue, action_queue_display, api_key, prompt_context,
           last_week, prev_week):

    # ── Story shell ───────────────────────────────────────────────────────
    p1_count = int((action_queue["Priority"] == "P1").sum()) if not action_queue.empty else 0
    late_context   = f"{fl_on_time:.1f}% on time" if fl_on_time else "real data pending"
    repeat_context = f"{ret_repeat:.1f}% repeat"  if ret_repeat  else "real data pending"

    if action_queue.empty:
        top_leak   = "Run the data build"
        top_owner  = "Ops"
        top_impact = "Pending"
        top_action = "Generate the real-data files to populate the operating story."
    else:
        top_row    = action_queue.iloc[0]
        top_leak   = escape(str(top_row["Leak"]))
        top_owner  = escape(str(top_row["Owner"]))
        top_impact = brl(top_row["Impact"])
        top_action = escape(str(top_row["Recommended action"]))

    # ── Three-stage system frame ──────────────────────────────────────────
    st.markdown("""
<div style="display:flex;gap:0;margin:0 0 20px;border:1px solid #1c1c2a;border-radius:10px;overflow:hidden">
  <div style="flex:1;padding:14px 18px;border-right:1px solid #1c1c2a">
    <p style="color:#7c6bff;font-family:monospace;font-size:9px;letter-spacing:.12em;text-transform:uppercase;margin:0 0 4px">Stage 1</p>
    <p style="color:#eeeeff;font-weight:700;font-size:14px;margin:0 0 3px">Data Foundation</p>
    <p style="color:#5a5a7a;font-size:11px;margin:0">Reconcile sources. Establish ground truth. Map what each gap costs.</p>
  </div>
  <div style="flex:1;padding:14px 18px;border-right:1px solid #1c1c2a;background:#0f0f18">
    <p style="color:#22d3a0;font-family:monospace;font-size:9px;letter-spacing:.12em;text-transform:uppercase;margin:0 0 4px">Stage 2 · You are here</p>
    <p style="color:#eeeeff;font-weight:700;font-size:14px;margin:0 0 3px">Intelligence</p>
    <p style="color:#5a5a7a;font-size:11px;margin:0">Prioritised action queue. Revenue impact per leak. Monthly AI brief.</p>
  </div>
  <div style="flex:1;padding:14px 18px">
    <p style="color:#f5c542;font-family:monospace;font-size:9px;letter-spacing:.12em;text-transform:uppercase;margin:0 0 4px">Stage 3</p>
    <p style="color:#eeeeff;font-weight:700;font-size:14px;margin:0 0 3px">Automations</p>
    <p style="color:#5a5a7a;font-size:11px;margin:0">Agents that watch conditions and take operational actions — not another report.</p>
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="story-shell">
      <div class="story-header">
        <div>
          <p class="kpi-label" style="margin:0 0 6px">{RETAILER_NAME} · operating story</p>
          <p class="story-title">You're spending to acquire customers you can't keep.</p>
          <p class="story-copy">Media spend looks productive. Platforms overclaim. Fulfillment erodes reviews. And most buyers never come back. The leak isn't in the ads — it's in everything after the click.</p>
        </div>
      </div>
      <div class="story-rail">
        <div class="story-beat" style="--beat-color:#7c6bff">
          <p class="story-label">Spend</p>
          <p class="story-number">{avg_mer:.2f}x MER</p>
          <p class="story-line">R${total_spend/1e6:.1f}M in media spend. Platforms claim +{overclaim_pct:.0f}% above Shopify truth.</p>
        </div>
        <div class="story-arrow">→</div>
        <div class="story-beat" style="--beat-color:#22d3a0">
          <p class="story-label">Delivery</p>
          <p class="story-number">{late_context}</p>
          <p class="story-line">{f'{fl_orders_k:.0f}k orders, {fl_days:.1f} day average delivery.' if fl_on_time else 'Build Olist files for fulfillment coverage.'}</p>
        </div>
        <div class="story-arrow">→</div>
        <div class="story-beat" style="--beat-color:#f5c542">
          <p class="story-label">Repeat</p>
          <p class="story-number">{repeat_context}</p>
          <p class="story-line">{f'{ret_customers_k:.0f}k customers, R${ret_ltv:.0f} average 180d LTV.' if ret_repeat else 'Build Olist files for cohort coverage.'}</p>
        </div>
      </div>
      <div class="story-action">
        <div>
          <p class="story-action-title">Next move: {top_leak}</p>
          <p class="story-action-copy">{top_owner} owns {top_impact} of estimated impact. {top_action}</p>
        </div>
        <div class="story-pill">{p1_count} P1 leaks</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Opportunities ─────────────────────────────────────────────────────
    st.markdown("### Opportunities")
    st.markdown('<p style="color:#8d8daf;font-size:14px;margin:-8px 0 24px">Ranked by estimated revenue impact. Each one has a named owner and a specific action — not a suggestion to investigate.</p>', unsafe_allow_html=True)

    if action_queue_display.empty:
        st.info("Run `python scripts/build_olist_data.py` to populate the opportunity queue.", icon="⚙️")
    else:
        total_impact = action_queue["Impact"].sum()
        p1_items     = action_queue[action_queue["Priority"] == "P1"]
        p1_impact    = p1_items["Impact"].sum()

        roll_cols = st.columns(3)
        roll_cols[0].metric("Total identified opportunity", brl(total_impact))
        roll_cols[1].metric("Urgent (act this week)", brl(p1_impact), f"{len(p1_items)} items")
        roll_cols[2].metric("Items in queue", str(len(action_queue_display)))

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        for _, row in action_queue.head(6).iterrows():
            owner       = str(row["Owner"])
            leak        = escape(str(row["Leak"]))
            action_text = escape(str(row["Recommended action"]))
            confidence  = escape(str(row["Confidence"]))
            source      = escape(str(row["Source"]))
            priority    = str(row["Priority"])
            impact_val  = brl(row["Impact"])

            color = "#7c6bff"
            if "Ops" in owner:         color = "#22d3a0"
            elif "Retention" in owner: color = "#f5c542"
            elif "Finance" in owner:   color = "#ff5566"

            priority_label = "Act this week" if priority == "P1" else "Act this month"

            st.markdown(f"""
<div style="background:#0d0d1a;border:1px solid #1c1c2a;border-left:5px solid {color};border-radius:10px;padding:24px 28px;margin-bottom:16px">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px;flex-wrap:wrap;gap:12px">
    <div>
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
        <span style="background:{color}20;color:{color};border:1px solid {color}44;border-radius:4px;padding:2px 10px;font-family:monospace;font-size:10px;letter-spacing:.1em;text-transform:uppercase">{priority_label}</span>
        <span style="color:#3a3a5a;font-size:11px;font-family:monospace">{source}</span>
      </div>
      <p style="color:#eeeeff;font-size:20px;font-weight:800;margin:0;line-height:1.2">{leak}</p>
    </div>
    <div style="text-align:right;flex-shrink:0">
      <p style="font-family:monospace;font-size:10px;color:#5a5a7a;text-transform:uppercase;letter-spacing:.1em;margin:0 0 4px">Estimated impact</p>
      <p style="color:{color};font-size:32px;font-weight:900;margin:0;line-height:1">{impact_val}</p>
    </div>
  </div>
  <p style="color:#b0b0d0;font-size:14px;line-height:1.7;margin:0 0 16px;max-width:780px">{action_text}</p>
  <div style="display:flex;gap:24px;padding-top:14px;border-top:1px solid #1c1c2a;font-size:11px;font-family:monospace;flex-wrap:wrap">
    <span style="color:#5a5a7a">Owner: <strong style="color:#9090b8">{escape(owner)}</strong></span>
    <span style="color:#5a5a7a">Confidence: <strong style="color:#9090b8">{confidence}</strong></span>
  </div>
</div>
""", unsafe_allow_html=True)

    st.divider()

    # ── AI Brief ──────────────────────────────────────────────────────────
    st.markdown("### AI-generated brief")
    st.markdown("""
<div class="callout">
Turns the opportunity queue above into a plain-language weekly brief — 600 words, no prep time.
Demo mode runs without an API key.
</div>
""", unsafe_allow_html=True)

    cta_left, cta_mid, cta_right = st.columns([0.22, 0.16, 0.62])
    with cta_left:
        generate_btn = st.button("Generate brief", type="primary", use_container_width=True, key="ai_generate")
    with cta_mid:
        demo_btn = st.button("Show demo", use_container_width=True, key="ai_demo")
    with cta_right:
        st.caption("Paste your OpenAI key in the sidebar to generate a live brief from the current numbers.")
    brief_placeholder = st.empty()
    if generate_btn:
        generate_openai_brief(api_key, prompt_context, brief_placeholder)
    elif demo_btn:
        brief_placeholder.markdown(render_brief_box(DEMO_BRIEF), unsafe_allow_html=True)

    st.divider()
