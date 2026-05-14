"""
Data Foundation — Stage 1
Before we can find the leaks, we need to know which numbers to trust.
"""
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from shared import plot_layout, COLORS, brl


def render(weekly, cohorts_real, fl_monthly, seller_perf, pay_by_type,
           cb_monthly_df, season_monthly, returns):

    # ── Stage frame ───────────────────────────────────────────────────────
    st.markdown("""
<div class="ai-hero">
  <p class="ai-hero-title">Stage 1 — Data Foundation</p>
  <p class="ai-status">
    Most Shopify brands have five data sources reporting different numbers for the same events.
    Before any intelligence is possible, the data has to be trustworthy.
    This section shows the audit: what each source claims, where the conflicts are,
    and what it costs to ignore them.
  </p>
</div>
""", unsafe_allow_html=True)

    # ── The three-stage pipeline ──────────────────────────────────────────
    st.markdown(f"""
<div class="story-rail" style="margin:0 0 24px">
  <div class="story-beat" style="--beat-color:#7c6bff">
    <p class="story-label">Stage 1 · You are here</p>
    <p class="story-number" style="font-size:22px">Data Foundation</p>
    <p class="story-line">Audit sources. Establish ground truth. Map what's connected, what's broken, and what each gap costs.</p>
  </div>
  <div class="story-arrow">→</div>
  <div class="story-beat" style="--beat-color:#22d3a0">
    <p class="story-label">Stage 2</p>
    <p class="story-number" style="font-size:22px">Intelligence</p>
    <p class="story-line">Monthly dashboard + AI brief. Prioritised action queue with revenue impact per leak.</p>
  </div>
  <div class="story-arrow">→</div>
  <div class="story-beat" style="--beat-color:#f5c542">
    <p class="story-label">Stage 3</p>
    <p class="story-number" style="font-size:22px">Automations</p>
    <p class="story-line">Discrete agents that watch conditions and take operational actions — not another report.</p>
  </div>
</div>
""", unsafe_allow_html=True)

    st.divider()

    # ── Section 1: The attribution conflict ───────────────────────────────
    st.markdown("### Why can't we trust platform-reported revenue?")
    st.markdown(
        '<p style="color:#8d8daf;font-size:14px;margin:-8px 0 16px">'
        "Meta, Google, and Email each use their own attribution model. "
        "Each claims the same customer as their own win. "
        "One sale. Three winners. The math doesn't add up — and it costs you money when it doesn't."
        "</p>",
        unsafe_allow_html=True,
    )

    total_rev     = weekly["shopify_revenue"].sum()
    total_claimed = weekly["total_claimed"].sum()
    overclaim_pct = (total_claimed / total_rev - 1) * 100 if total_rev else 0
    phantom       = total_claimed - total_rev

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        "What Shopify recorded", brl(total_rev),
        help="Gross revenue per Shopify orders — the ground truth. This is the number that matches your bank account.",
    )
    c2.metric(
        "What platforms claim", brl(total_claimed),
        help="Sum of revenue each ad platform takes credit for. "
             "Because each uses its own attribution window, the same order is counted multiple times.",
        delta_color="inverse",
    )
    c3.metric(
        "Overclaim gap", f"+{overclaim_pct:.0f}%",
        help="How much more platforms claim vs what Shopify recorded. "
             "Platforms aren't lying — they're using different rules. The problem is that none of them match reality.",
        delta_color="inverse",
    )
    c4.metric(
        "Phantom revenue", brl(phantom),
        f"over {len(weekly)} weeks",
        help="Revenue claimed by platforms that Shopify did not record. "
             "Budget decisions made from platform dashboards alone are made on numbers this much larger than reality.",
        delta_color="inverse",
    )

    col_at1, col_at2 = st.columns([3, 2])
    with col_at1:
        fig_conflict = go.Figure()
        fig_conflict.add_trace(go.Bar(
            x=weekly["week_start"], y=weekly["shopify_revenue"],
            name="Shopify (ground truth)", marker_color=COLORS["shopify"], opacity=0.9,
        ))
        fig_conflict.add_trace(go.Scatter(
            x=weekly["week_start"], y=weekly["total_claimed"],
            name="Platforms' combined claim", mode="lines",
            line=dict(color=COLORS["claimed"], width=2, dash="dot"),
        ))
        fig_conflict.update_layout(**plot_layout(
            title="Weekly: what Shopify recorded vs what platforms claim",
            barmode="overlay", height=300,
            legend=dict(orientation="h", y=1.15),
        ))
        st.plotly_chart(fig_conflict, use_container_width=True)

    with col_at2:
        avg_google_rep  = (weekly["google_reported_revenue"] / weekly["google_spend"]).mean()
        avg_meta_rep    = (weekly["meta_reported_revenue"]   / weekly["meta_spend"]).mean()
        avg_google_true = (weekly["google_true"] / weekly["google_spend"]).mean()
        avg_meta_true   = (weekly["meta_true"]   / weekly["meta_spend"]).mean()

        st.markdown(f"""
<div style="display:flex;flex-direction:column;gap:10px;margin-top:8px">
  <div style="background:#0f0f18;border:1px solid #1c1c2a;border-radius:8px;padding:14px 16px">
    <p class="kpi-label" style="margin:0 0 4px">Google Ads</p>
    <p style="color:#3b9eff;font-size:22px;font-weight:800;margin:0">
      {avg_google_rep:.1f}x claimed
      <span style="color:#22d3a0;font-size:16px;font-weight:600"> vs {avg_google_true:.1f}x actual</span>
    </p>
    <p style="color:#5a5a78;font-size:11px;margin:4px 0 0">
      ~{(avg_google_rep/avg_google_true - 1)*100:.0f}% overclaim — PMax cross-channel double-counting + data-driven attribution
    </p>
  </div>
  <div style="background:#0f0f18;border:1px solid #1c1c2a;border-radius:8px;padding:14px 16px">
    <p class="kpi-label" style="margin:0 0 4px">Meta Ads</p>
    <p style="color:#ff6b6b;font-size:22px;font-weight:800;margin:0">
      {avg_meta_rep:.1f}x claimed
      <span style="color:#22d3a0;font-size:16px;font-weight:600"> vs {avg_meta_true:.1f}x actual</span>
    </p>
    <p style="color:#5a5a78;font-size:11px;margin:4px 0 0">
      ~{(avg_meta_rep/avg_meta_true - 1)*100:.0f}% overclaim — 7-day click / 1-day view window + iOS modelled conversions
    </p>
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div class="callout callout-red">
<strong>Why this matters for budgeting:</strong> If you scale spend based on platform-reported ROAS,
you're optimising toward a number that's systematically inflated.
The Data Foundation establishes <strong>Shopify as ground truth</strong> and replaces platform dashboards
with a single blended metric — total revenue ÷ total spend — that doesn't depend on any platform's attribution model.
</div>
""", unsafe_allow_html=True)

    st.divider()

    # ── Section 2: GA4 gap ────────────────────────────────────────────────
    st.markdown("### Why does Google Analytics show less revenue than Shopify?")

    avg_ga4_miss = weekly["ga4_missing_pct"].mean()

    col_ga1, col_ga2 = st.columns([3, 2])
    with col_ga1:
        fig_ga4 = go.Figure()
        fig_ga4.add_trace(go.Scatter(
            x=weekly["week_start"], y=weekly["shopify_revenue"],
            name="Shopify", fill="tozeroy",
            line=dict(color=COLORS["shopify"], width=2),
            fillcolor="rgba(34,211,160,0.08)",
        ))
        fig_ga4.add_trace(go.Scatter(
            x=weekly["week_start"], y=weekly["ga4_revenue"],
            name="GA4", fill="tozeroy",
            line=dict(color="#888899", width=1.5, dash="dash"),
            fillcolor="rgba(136,136,153,0.06)",
        ))
        fig_ga4.update_layout(**plot_layout(
            title=f"GA4 tracking gap — analytics misses {avg_ga4_miss:.0f}% of revenue on average",
            height=280, legend=dict(orientation="h", y=1.15),
        ))
        st.plotly_chart(fig_ga4, use_container_width=True)

    with col_ga2:
        st.markdown(f"""
<div class="callout" style="margin-top:8px">
<strong>The four causes of the GA4 gap:</strong><br><br>
🔹 <strong>Ad blockers</strong> — 25–40% of ecommerce shoppers block client-side tracking<br><br>
🔹 <strong>Safari ITP</strong> — iOS caps first-party cookies at 7 days; returning buyers look like new sessions<br><br>
🔹 <strong>Payment redirects</strong> — PayPal, Klarna, Shop Pay leave the Shopify domain and kill the purchase event<br><br>
🔹 <strong>Checkout subdomain</strong> — Shopify's new checkout blocks GTM by default<br><br>
<strong>Fix:</strong> server-side GTM + Meta CAPI + Google Enhanced Conversions.
This is a Data Foundation deliverable.
</div>
""", unsafe_allow_html=True)

    st.divider()

    # ── Section 3: Data map ───────────────────────────────────────────────
    st.markdown("### What's connected, what's real, and what each gap costs")
    st.markdown(
        '<p style="color:#8d8daf;font-size:14px;margin:-8px 0 16px">'
        "A summary of every data source powering this dashboard — its origin, coverage, and status."
        "</p>",
        unsafe_allow_html=True,
    )

    DATA_MAP = [
        {
            "source": "Shopify",
            "what": "Orders, revenue, AOV",
            "type": "Synthetic (modeled on Olist)",
            "status": "connected",
            "cost_if_missing": "Can't establish ground truth — all other numbers float",
            "accent": "#22d3a0",
        },
        {
            "source": "Google Ads",
            "what": "Reported revenue, spend, campaign-level ROAS",
            "type": "Synthetic (real overclaim model)",
            "status": "connected",
            "cost_if_missing": f"~{(weekly['google_reported_revenue'].sum() / weekly['google_true'].sum() - 1)*100:.0f}% of budget decisions made on inflated numbers",
            "accent": "#3b9eff",
        },
        {
            "source": "Meta Ads",
            "what": "Reported revenue, spend, pixel attribution",
            "type": "Synthetic (iOS ATT modelled)",
            "status": "connected",
            "cost_if_missing": f"~{(weekly['meta_reported_revenue'].sum() / weekly['meta_true'].sum() - 1)*100:.0f}% of Meta budget allocated based on over-reported performance",
            "accent": "#ff6b6b",
        },
        {
            "source": "Google Analytics 4",
            "what": "Sessions, pageviews, purchase events",
            "type": "Synthetic (gap model)",
            "status": "gap",
            "cost_if_missing": f"{avg_ga4_miss:.0f}% of revenue invisible to analytics — funnel analysis is unreliable",
            "accent": "#f5c542",
        },
        {
            "source": "Fulfillment (Olist)",
            "what": "Delivery times, on-time rates, review scores",
            "type": "Real Olist dataset",
            "status": "connected" if fl_monthly is not None else "missing",
            "cost_if_missing": "Can't measure how late delivery damages reviews and repeat purchase",
            "accent": "#22d3a0",
        },
        {
            "source": "Customer cohorts (Olist)",
            "what": "Repeat purchase rates, LTV by acquisition month",
            "type": "Real Olist dataset",
            "status": "connected" if cohorts_real is not None else "missing",
            "cost_if_missing": "Can't see whether acquisition is compounding into repeat revenue",
            "accent": "#f5c542",
        },
        {
            "source": "Payments (Olist)",
            "what": "Payment type mix, installment counts, cancellation rates",
            "type": "Real Olist dataset",
            "status": "connected" if pay_by_type is not None else "missing",
            "cost_if_missing": "Can't identify orders at risk of non-payment or cancellation before shipping",
            "accent": "#ff8a4c",
        },
        {
            "source": "Sellers (Olist)",
            "what": "Seller revenue, review quality, on-time rate per seller",
            "type": "Real Olist dataset",
            "status": "connected" if seller_perf is not None else "missing",
            "cost_if_missing": "Can't catch seller SLA breaches before they accumulate into review damage",
            "accent": "#9b72cf",
        },
        {
            "source": "Dispute signals (Olist)",
            "what": "3-signal chargeback proxy: late + 1-star + high installments",
            "type": "Real Olist dataset",
            "status": "connected" if cb_monthly_df is not None else "missing",
            "cost_if_missing": f"{brl(cb_monthly_df['flagged_revenue'].sum() if cb_monthly_df is not None else 0)} in flagged revenue with no pre-shipment review",
            "accent": "#ff5566",
        },
    ]

    STATUS_BADGE = {
        "connected": ('<span style="background:#0d1a14;color:#22d3a0;border:1px solid #22d3a044;'
                      'border-radius:999px;padding:2px 10px;font-size:10px;font-family:monospace">● Connected</span>'),
        "gap":       ('<span style="background:#1a1500;color:#f5c542;border:1px solid #f5c54244;'
                      'border-radius:999px;padding:2px 10px;font-size:10px;font-family:monospace">◐ Gap detected</span>'),
        "missing":   ('<span style="background:#1a0d10;color:#ff5566;border:1px solid #ff556644;'
                      'border-radius:999px;padding:2px 10px;font-size:10px;font-family:monospace">○ Missing</span>'),
    }

    for row in DATA_MAP:
        badge = STATUS_BADGE.get(row["status"], "")
        st.markdown(f"""
<div style="display:flex;align-items:flex-start;gap:14px;padding:14px 0;
            border-bottom:1px solid #1c1c2a">
  <div style="width:4px;min-height:52px;background:{row['accent']};
              border-radius:2px;flex-shrink:0;margin-top:2px"></div>
  <div style="flex:1;min-width:0">
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;flex-wrap:wrap">
      <span style="color:#eeeeff;font-weight:700;font-size:15px">{row['source']}</span>
      {badge}
      <span style="color:#3a3a5a;font-size:11px;font-family:monospace">{row['type']}</span>
    </div>
    <p style="color:#8d8daf;font-size:13px;margin:0 0 4px">{row['what']}</p>
    <p style="color:#5a5a6a;font-size:12px;margin:0">
      <strong style="color:#6a4a4a">Without this:</strong> {row['cost_if_missing']}
    </p>
  </div>
</div>
""", unsafe_allow_html=True)

    st.divider()

    # ── Section 4: Technical schema (analyst deep-dive) ───────────────────
    with st.expander("Technical details — tables, columns, and sample data", expanded=False):
        st.markdown(
            '<p style="color:#8d8daf;font-size:13px;margin-bottom:16px">'
            "For analysts who want to verify methodology or extend the model."
            "</p>",
            unsafe_allow_html=True,
        )

        SCHEMA_CATALOGUE = [
            {
                "id": "weekly_synthetic",
                "label": "Weekly marketing data (synthetic)",
                "source": "data_gen.py  ·  seed=42",
                "df": weekly,
                "cols": ["week_start", "shopify_revenue", "total_spend",
                         "google_reported_revenue", "meta_reported_revenue",
                         "total_claimed", "mer", "ga4_revenue"],
            },
            {
                "id": "fulfillment_monthly",
                "label": "Fulfillment — monthly (real Olist)",
                "source": "data/fulfillment_monthly.csv",
                "df": fl_monthly,
                "cols": ["purchase_month", "orders", "on_time_rate",
                         "avg_delivery_days", "avg_review_score"],
            },
            {
                "id": "cohorts_real",
                "label": "Customer cohorts (real Olist)",
                "source": "data/cohorts_real.csv",
                "df": cohorts_real,
                "cols": ["cohort_month", "cohort_size", "ret_30d", "ret_180d",
                         "ltv_30d", "ltv_180d", "is_outlier"],
            },
            {
                "id": "returns_synthetic",
                "label": "Returns & refunds (synthetic)",
                "source": "data_gen.py  ·  seed=42",
                "df": returns,
                "cols": ["week_start", "category", "reason", "returns", "refund_value"],
            },
            {
                "id": "payments_by_type",
                "label": "Payments by type (real Olist)",
                "source": "data/payments_by_type.csv",
                "df": pay_by_type,
                "cols": ["payment_type", "orders", "cancelled", "cancellation_rate"],
            },
            {
                "id": "chargeback_monthly",
                "label": "Dispute risk — monthly (real Olist)",
                "source": "data/chargeback_monthly.csv",
                "df": cb_monthly_df,
                "cols": ["purchase_month", "total_orders", "flagged_orders", "flagged_revenue"],
            },
        ]

        for entry in SCHEMA_CATALOGUE:
            df = entry["df"]
            with st.expander(f"{entry['label']}  ·  `{entry['source']}`", expanded=False):
                if df is not None and not df.empty:
                    available = [c for c in entry["cols"] if c in df.columns]
                    st.dataframe(df[available].head(5), use_container_width=True, hide_index=True)
                    st.caption(f"{len(df):,} rows · {len(df.columns)} columns total")
                else:
                    st.markdown(
                        '<p style="color:#5a5a7a;font-size:13px">'
                        "Not available — run <code>scripts/build_olist_data.py</code></p>",
                        unsafe_allow_html=True,
                    )
