"""
Margin Intelligence Report
Retail operating dashboard demo — synthetic attribution modeled on Olist Brazil
"""

import streamlit as st
import pandas as pd
import numpy as np
import duckdb
from pathlib import Path
from data_gen import load_all

from shared import (
    CONSULTANCY_NAME, PRODUCT_NAME, RETAILER_NAME, RETAILER_CATEGORY, BRAND_PROMISE,
    brl,
)
import views.executive_brief as pg_brief
import views.demand as pg_demand
import views.sales as pg_sales
import views.spend as pg_spend
import views.delivery as pg_delivery
import views.customers as pg_customers
import views.payments as pg_payments
import views.sellers as pg_sellers
import views.risk as pg_risk
import views.agents as pg_agents
import views.categories as pg_categories

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Margin Intelligence Report",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Theme / CSS ────────────────────────────────────────────────────────────
st.markdown("""
<style>
  [data-testid="stAppViewContainer"] { background: #09090e; }
  [data-testid="stSidebar"]          { background: #0f0f18; border-right: 1px solid #1c1c2a; }
  [data-testid="stHeader"]           { background: transparent; }

  h1,h2,h3,h4 { color: #eeeeff !important; }
  p, li        { color: #a0a0c0; }
  label        { color: #7070a0 !important; }

  [data-testid="metric-container"] {
    background: #0f0f18;
    border: 1px solid #1c1c2a;
    border-radius: 10px;
    padding: 14px 18px;
  }
  [data-testid="metric-container"] [data-testid="stMetricLabel"]  { color: #6060a0 !important; font-size: 11px; }
  [data-testid="metric-container"] [data-testid="stMetricValue"]  { color: #eeeeff !important; }
  [data-testid="metric-container"] [data-testid="stMetricDelta"]  { font-size: 11px; }

  [data-baseweb="tab-list"]  { background: #0f0f18; border-bottom: 1px solid #1c1c2a; gap: 6px; padding: 8px 6px 0; }
  [data-baseweb="tab"]       { background: transparent; color: #6060a0; border-radius: 6px 6px 0 0;
                               padding: 10px 22px !important; font-size: 13px !important;
                               letter-spacing: 0.015em; }
  [aria-selected="true"]     { background: #1a1a28 !important; color: #eeeeff !important; }

  /* Column gap — gives charts breathing room */
  [data-testid="stHorizontalBlock"] { gap: 28px !important; }

  /* Section headings */
  h2 { margin-top: 8px !important; margin-bottom: 12px !important; }
  h3 { margin-top: 8px !important; margin-bottom: 12px !important; }
  h4 { margin-top: 16px !important; margin-bottom: 10px !important; }

  /* kpi-label captions that precede charts or sections */
  .kpi-label { margin-bottom: 10px !important; }

  /* Push chart containers down from whatever precedes them */
  [data-testid="stPlotlyChart"]  { margin-top: 16px !important; }
  [data-testid="stDataFrame"]    { margin-top: 10px !important; }

  /* Divider breathing room */
  [data-testid="stDivider"] { margin: 32px 0 !important; }

  .callout {
    background: #12122a;
    border-left: 3px solid #7c6bff;
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    margin: 8px 0;
    font-size: 13px;
    line-height: 1.7;
    color: #b0b0d0;
  }
  .callout-red   { border-left-color: #ff5566; background: #1a0d10; color: #d0b0b5; }
  .callout-green { border-left-color: #22d3a0; background: #0d1a14; color: #b0d0c5; }
  .callout-amber { border-left-color: #f5c542; background: #1a1500; color: #d0c090; }

  .pillar-section {
    border-top: 1px solid #1c1c2a;
    margin: 24px 0 16px;
    padding-top: 16px;
  }

  .kpi-label { font-family: monospace; font-size: 10px; color: #5a5a78;
               letter-spacing: .1em; text-transform: uppercase; }

  .brief-box {
    background: #0d0d18;
    border: 1px solid #2a2a40;
    border-radius: 10px;
    padding: 20px 24px;
    font-size: 14px;
    line-height: 1.8;
    color: #c0c0e0;
    white-space: pre-wrap;
  }

  .brand-card {
    background: #0f0f18;
    border: 1px solid #1c1c2a;
    border-radius: 10px;
    padding: 16px 18px;
  }
  .brand-lockup {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 10px;
  }
  .brand-mark {
    width: 42px;
    height: 42px;
    border-radius: 8px;
    display: grid;
    place-items: center;
    color: #09090e;
    background: linear-gradient(135deg, #22d3a0 0%, #f5c542 52%, #7c6bff 100%);
    font-weight: 900;
    font-size: 18px;
    letter-spacing: 0;
  }
  .brand-name {
    color: #eeeeff;
    font-size: 20px;
    font-weight: 800;
    line-height: 1.1;
  }
  .brand-subtitle {
    color: #6060a0;
    font-size: 10px;
    letter-spacing: .12em;
    text-transform: uppercase;
    margin-top: 3px;
    font-family: monospace;
  }
  .product-chip {
    display: inline-block;
    border: 1px solid #2a2a40;
    color: #a0a0c0;
    background: #09090e;
    border-radius: 999px;
    padding: 5px 10px;
    margin: 0 6px 6px 0;
    font-size: 11px;
  }
  .ai-hero {
    background: #101026;
    border: 1px solid #2a2a55;
    border-left: 4px solid #7c6bff;
    border-radius: 10px;
    padding: 18px 20px;
    margin: 14px 0 18px;
  }
  .ai-hero-title {
    color: #eeeeff;
    font-size: 20px;
    font-weight: 800;
    margin: 0 0 4px;
  }
	  .ai-status {
	    color: #a0a0c0;
	    font-size: 12px;
	    line-height: 1.6;
	  }
	  .ai-status strong { color: #eeeeff; }

	  .story-shell {
	    margin: 12px 0 22px;
	    padding: 22px 4px 8px;
	    border-top: 1px solid #202034;
	    border-bottom: 1px solid #202034;
	  }
	  .story-header {
	    display: flex;
	    justify-content: space-between;
	    align-items: flex-start;
	    gap: 28px;
	    margin-bottom: 22px;
	  }
	  .story-title {
	    color: #eeeeff;
	    font-size: 34px;
	    font-weight: 900;
	    line-height: 1.08;
	    max-width: 680px;
	    margin: 0 0 8px;
	  }
	  .story-copy {
	    color: #8d8daf;
	    font-size: 14px;
	    line-height: 1.6;
	    max-width: 700px;
	    margin: 0;
	  }
	  .story-ai {
	    min-width: 250px;
	    padding-top: 4px;
	  }
	  .story-rail {
	    display: grid;
	    grid-template-columns: minmax(0, 1fr) 38px minmax(0, 1fr) 38px minmax(0, 1fr);
	    gap: 0;
	    align-items: center;
	    margin: 14px 0 18px;
	  }
	  .story-beat {
	    padding: 4px 0 10px;
	    border-top: 3px solid var(--beat-color);
	  }
	  .story-label {
	    color: var(--beat-color);
	    font-family: monospace;
	    font-size: 10px;
	    letter-spacing: .12em;
	    text-transform: uppercase;
	    margin: 10px 0 8px;
	  }
	  .story-number {
	    color: #eeeeff;
	    font-size: 32px;
	    font-weight: 900;
	    line-height: 1;
	    margin: 0 0 8px;
	  }
	  .story-line {
	    color: #8d8daf;
	    font-size: 12px;
	    line-height: 1.45;
	    margin: 0;
	  }
	  .story-arrow {
	    color: #3a3a5f;
	    font-size: 28px;
	    font-weight: 900;
	    text-align: center;
	  }
	  .story-action {
	    display: flex;
	    justify-content: space-between;
	    gap: 24px;
	    align-items: center;
	    padding-top: 14px;
	    border-top: 1px solid #1c1c2a;
	  }
	  .story-action-title {
	    color: #eeeeff;
	    font-size: 16px;
	    font-weight: 850;
	    margin: 0 0 4px;
	  }
	  .story-action-copy {
	    color: #8d8daf;
	    font-size: 12px;
	    line-height: 1.5;
	    margin: 0;
	  }
	  .story-pill {
	    color: #d8d8f0;
	    border: 1px solid #343456;
	    border-radius: 999px;
	    padding: 7px 11px;
	    font-size: 11px;
	    white-space: nowrap;
	  }
	  @media (max-width: 900px) {
	    .story-header, .story-action { display: block; }
	    .story-ai { min-width: 0; margin-top: 16px; }
	    .story-rail { grid-template-columns: 1fr; gap: 12px; }
	    .story-arrow { transform: rotate(90deg); }
	  }

	  #MainMenu, footer, header { visibility: hidden; }
  hr { border-color: #1c1c2a; }

  /* ── Sidebar nav buttons ───────────────────────────────────────────── */
  [data-testid="stSidebar"] .stButton {
    margin: 1px 0 !important;
  }
  [data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: none !important;
    border-left: 3px solid transparent !important;
    border-radius: 0 6px 6px 0 !important;
    color: #5a5a7a !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    text-align: left !important;
    justify-content: flex-start !important;
    padding: 8px 14px !important;
    width: 100% !important;
    box-shadow: none !important;
    transition: background 0.12s, color 0.12s, border-color 0.12s !important;
  }
  [data-testid="stSidebar"] .stButton > button:hover {
    background: #13131f !important;
    color: #c0c0e0 !important;
    border-left-color: #2a2a44 !important;
  }
  [data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {
    background: #16162a !important;
    color: #eeeeff !important;
    border-left-color: #7c6bff !important;
    font-weight: 700 !important;
  }
  [data-testid="stSidebar"] [data-testid="stBaseButton-primary"]:hover {
    background: #1c1c36 !important;
  }
  .nav-section-label {
    font-family: monospace;
    font-size: 9px;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: #2e2e48;
    padding: 10px 14px 4px;
  }
</style>
""", unsafe_allow_html=True)

# ── Load data ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    weekly, cohorts, categories, reviews, geo, returns = load_all(seed=42)
    return weekly, cohorts, categories, reviews, geo, returns

weekly, cohorts, categories, reviews, geo, returns = load_data()


@st.cache_data
def load_fulfillment_data():
    d = Path("data")
    needed = ["fulfillment_review_lateness.csv", "fulfillment_by_category.csv", "fulfillment_monthly.csv"]
    if not all((d / f).exists() for f in needed):
        return None, None, None
    return (
        pd.read_csv(d / "fulfillment_review_lateness.csv"),
        pd.read_csv(d / "fulfillment_by_category.csv"),
        pd.read_csv(d / "fulfillment_monthly.csv"),
    )


@st.cache_data
def load_geo_real():
    p = Path("data/geo_state_real.csv")
    return pd.read_csv(p) if p.exists() else None


fl_review_lateness, fl_by_category, fl_monthly = load_fulfillment_data()
geo_real = load_geo_real()


def _real(filename):
    p = Path("data") / filename
    return pd.read_csv(p) if p.exists() else None


rv_distribution    = _real("reviews_distribution.csv")
rv_monthly         = _real("reviews_monthly.csv")
rv_by_category     = _real("reviews_by_category.csv")
pay_by_type        = _real("payments_by_type.csv")
pay_installments   = _real("payments_installments.csv")
pay_by_category    = _real("payments_by_category.csv")
pay_by_state       = _real("payments_by_state.csv")
seller_perf        = _real("seller_performance.csv")
seller_conc        = _real("seller_concentration.csv")
cohorts_real       = _real("cohorts_real.csv")
season_monthly     = _real("seasonality_monthly.csv")
season_cat_monthly = _real("seasonality_cat_monthly.csv")
cb_monthly_df      = _real("chargeback_monthly.csv")
cb_category_df     = _real("chargeback_by_category.csv")
cb_evidence_df     = _real("chargeback_evidence.csv")

con = duckdb.connect()
con.register("weekly",     weekly)
con.register("cohorts",    cohorts)
con.register("categories", categories)
con.register("reviews",    reviews)
con.register("geo",        geo)
con.register("returns",    returns)

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
<div class="brand-card">
  <div class="brand-lockup">
    <div class="brand-mark">L</div>
    <div>
      <div class="brand-name">{RETAILER_NAME}</div>
      <div class="brand-subtitle">Mock Retail Client</div>
    </div>
  </div>
  <p style="color:#a0a0c0;font-size:12px;line-height:1.55;margin:0">{RETAILER_CATEGORY}</p>
</div>
""", unsafe_allow_html=True)
    st.markdown(f'<p class="kpi-label" style="margin-top:12px">{PRODUCT_NAME} · by {CONSULTANCY_NAME}</p>', unsafe_allow_html=True)
    st.divider()
# ── Navigation ─────────────────────────────────────────────────────────────
    NAV_ITEMS = [
        ("🤖 Executive Brief",  "overview"),
        ("📈 Revenue",          "overview"),
        ("🏷️ Categories",       "overview"),
        ("📅 Demand",           "overview"),
        ("🎯 Attribution",      "overview"),
        ("🔄 Retention",        "overview"),
        ("🚚 Fulfillment",      "overview"),
        ("💳 Payments",         "overview"),
        ("🏪 Sellers",          "overview"),
        ("🚨 Risk",             "overview"),
        ("🔮 Agent Prototypes", "agents"),
    ]
    if "page" not in st.session_state:
        st.session_state.page = "🤖 Executive Brief"

    prev_section = None
    for label, section in NAV_ITEMS:
        if section != prev_section and prev_section is not None:
            st.sidebar.markdown('<div class="nav-section-label">AI Layer</div>', unsafe_allow_html=True)
        prev_section = section
        is_active = st.session_state.page == label
        if st.sidebar.button(label, key=f"nav_{label}", use_container_width=True,
                             type="primary" if is_active else "secondary"):
            st.session_state.page = label
            st.rerun()

    page = st.session_state.page

    min_date = weekly["week_start"].min().date()
    max_date = weekly["week_start"].max().date()
    date_options = sorted(weekly["week_start"].dt.date.unique())
    cutoff_date = max(min_date, (pd.Timestamp(max_date) - pd.DateOffset(months=12)).date())
    default_start = next((d for d in date_options if d >= cutoff_date), min_date)

    date_range = st.select_slider(
        "Period",
        options=date_options,
        value=(default_start, max_date),
        format_func=lambda d: d.strftime("%b %Y"),
    )

    st.divider()
    st.markdown("### AI Brief Studio")
    api_key = st.text_input(
        "OpenAI API key",
        type="password",
        placeholder="sk-...",
        help="Optional. Live generation uses gpt-4o-mini; demo mode still works when quota is unavailable.",
    )
    st.caption("Live mode uses OpenAI's open-weight gpt-4o-mini model. Demo mode stays visible during quota issues.")

    st.divider()
    st.markdown("""
<p style="font-size:11px;color:#444466;line-height:1.7">
<strong style="color:#6666aa">Data note</strong><br>
Attribution uses synthetic Luma data modeled on Olist. Fulfillment, Geography,
Reviews, and Cohorts use the real Olist dataset.
</p>
""", unsafe_allow_html=True)

# ── Filter data ────────────────────────────────────────────────────────────
start_ts = pd.Timestamp(date_range[0])
end_ts   = pd.Timestamp(date_range[1])
wf        = weekly[(weekly["week_start"] >= start_ts) & (weekly["week_start"] <= end_ts)].copy()
cf        = categories[(categories["week_start"] >= start_ts) & (categories["week_start"] <= end_ts)].copy()
reviews_f = reviews[(reviews["week_start"] >= start_ts) & (reviews["week_start"] <= end_ts)].copy()
returns_f = returns[(returns["week_start"] >= start_ts) & (returns["week_start"] <= end_ts)].copy()

# ── Header ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:24px;margin-bottom:8px">
  <div>
    <div class="brand-lockup" style="margin-bottom:8px">
      <div class="brand-mark">L</div>
      <div>
        <div class="brand-name" style="font-size:28px">{RETAILER_NAME}</div>
        <div class="brand-subtitle">{RETAILER_CATEGORY}</div>
      </div>
    </div>
    <h1 style="margin:0;color:#eeeeff">{PRODUCT_NAME}</h1>
    <p style="color:#a0a0c0;margin:6px 0 0;max-width:760px">{BRAND_PROMISE}</p>
  </div>
  <div class="brand-card" style="min-width:250px">
    <p class="kpi-label" style="margin:0 0 6px">Packaged by</p>
    <p style="color:#eeeeff;font-size:18px;font-weight:800;margin:0">{CONSULTANCY_NAME}</p>
    <p style="color:#6060a0;font-size:11px;line-height:1.6;margin:8px 0 0">Operating analytics product for ecommerce leadership teams.</p>
  </div>
</div>
<p class="kpi-label">{RETAILER_NAME} · {date_range[0].strftime("%b %Y")} — {date_range[1].strftime("%b %Y")} · BRL · demo identity</p>
""", unsafe_allow_html=True)

# ── Core period metrics ────────────────────────────────────────────────────
total_rev     = wf["shopify_revenue"].sum()
total_spend   = wf["total_spend"].sum()
avg_mer       = total_rev / total_spend
total_claimed = wf["total_claimed"].sum()
overclaim_pct = (total_claimed / total_rev - 1) * 100
avg_ga4_miss  = wf["ga4_missing_pct"].mean()
last_mer      = wf.iloc[-1]["mer"]
prev_mer      = wf.iloc[-5]["mer"] if len(wf) > 5 else last_mer
if "anomaly" not in wf.columns:
    wf["mer_baseline"] = wf["mer"].rolling(8, min_periods=3).mean()
    wf["mer_std"]      = wf["mer"].rolling(8, min_periods=3).std()
    wf["mer_lower"]    = wf["mer_baseline"] - 1.5 * wf["mer_std"]
    wf["mer_upper"]    = wf["mer_baseline"] + 1.5 * wf["mer_std"]
    wf["anomaly"]      = (wf["mer"] < wf["mer_lower"]) | (wf["mer"] > wf["mer_upper"])

# ── Pillar KPIs for operating flow ────────────────────────────────────────
_fl_on_time = _fl_days = _fl_orders_k = None
if fl_monthly is not None:
    _fw = fl_monthly["orders"]
    _fl_on_time    = np.average(fl_monthly["on_time_rate"],      weights=_fw) * 100
    _fl_days       = np.average(fl_monthly["avg_delivery_days"], weights=_fw)
    _fl_orders_k   = fl_monthly["orders"].sum() / 1000

_ret_repeat = _ret_ltv = _ret_customers_k = None
if cohorts_real is not None:
    _sz = cohorts_real["cohort_size"]
    _ret_repeat       = (cohorts_real["ret_180d"] * _sz).sum() / _sz.sum() * 100
    _ret_ltv          = cohorts_real["ltv_180d"].mean()
    _ret_customers_k  = _sz.sum() / 1000

# ── Action queue ──────────────────────────────────────────────────────────
action_rows = []
phantom_revenue = max(total_claimed - total_rev, 0)
if phantom_revenue > 0:
    meta_true    = wf["meta_true"].sum()
    google_true  = wf["google_true"].sum()
    meta_overclaim   = (wf["meta_reported_revenue"].sum()   / meta_true   - 1) * 100 if meta_true   else 0
    google_overclaim = (wf["google_reported_revenue"].sum() / google_true - 1) * 100 if google_true else 0
    worst_channel = "Meta" if meta_overclaim >= google_overclaim else "Google"
    action_rows.append({
        "Priority": "P1",
        "Leak": "Platform overclaim",
        "Impact": phantom_revenue,
        "Owner": "Growth",
        "Recommended action": f"Use MER as the spend guardrail; cut {worst_channel} by 10-15% until incrementality is proven.",
        "Confidence": "High",
        "Source": "Synthetic attribution",
    })

if fl_review_lateness is not None and fl_by_category is not None:
    late_orders = int(fl_review_lateness.loc[fl_review_lateness["bucket"] != "On time", "order_count"].sum())
    avg_order_value_real = fl_by_category["revenue"].sum() / fl_by_category["orders"].sum()
    late_revenue_proxy   = late_orders * avg_order_value_real
    action_rows.append({
        "Priority": "P1",
        "Leak": "Late delivery review damage",
        "Impact": late_revenue_proxy,
        "Owner": "Ops",
        "Recommended action": f"Create an SLA recovery queue for {late_orders:,} late orders; trigger customer outreach after day 3 late.",
        "Confidence": "High",
        "Source": "Fulfillment + reviews",
    })

if cohorts_real is not None:
    cohort_customers       = cohorts_real["cohort_size"].sum()
    repeat_rate            = (cohorts_real["ret_180d"] * cohorts_real["cohort_size"]).sum() / cohort_customers
    target_repeat          = 0.05
    incremental_customers  = max(target_repeat - repeat_rate, 0) * cohort_customers
    retention_upside       = incremental_customers * cohorts_real["ltv_180d"].mean()
    action_rows.append({
        "Priority": "P1",
        "Leak": "One-time buyer churn",
        "Impact": retention_upside,
        "Owner": "Retention",
        "Recommended action": f"Launch a 45-day second-purchase flow; move 180d repeat from {repeat_rate * 100:.1f}% toward 5.0%.",
        "Confidence": "Medium",
        "Source": "Cohorts",
    })

if cb_monthly_df is not None and cb_category_df is not None:
    cb_risk    = cb_monthly_df["flagged_revenue"].sum()
    top_cb_cat = cb_category_df.iloc[0]["primary_category"]
    action_rows.append({
        "Priority": "P2",
        "Leak": "Chargeback exposure",
        "Impact": cb_risk,
        "Owner": "Finance",
        "Recommended action": f"Manually review 2+ signal orders in {top_cb_cat}; require evidence capture before shipment.",
        "Confidence": "Medium",
        "Source": "Risk signals",
    })

if pay_installments is not None:
    high_risk_payment = pay_installments.sort_values("cancellation_rate", ascending=False).iloc[0]
    payment_impact    = high_risk_payment["orders"] * high_risk_payment["avg_value"] * high_risk_payment["cancellation_rate"]
    action_rows.append({
        "Priority": "P2",
        "Leak": "Payment cancellation risk",
        "Impact": payment_impact,
        "Owner": "Finance",
        "Recommended action": f"Add extra confirmation for {high_risk_payment['installment_bucket']} installments before release to fulfillment.",
        "Confidence": "Medium",
        "Source": "Payments",
    })

if seller_perf is not None:
    seller_priority = (
        seller_perf[(seller_perf["orders"] >= 50) & (seller_perf["avg_review_score"] < 3.7)]
        .sort_values("revenue", ascending=False)
    )
    if not seller_priority.empty:
        seller_row = seller_priority.iloc[0]
        action_rows.append({
            "Priority": "P2",
            "Leak": "Seller quality drag",
            "Impact": seller_row["revenue"],
            "Owner": "Marketplace Ops",
            "Recommended action": f"Review seller {seller_row['seller_id'][:8]}...; enforce SLA plan or suppress low-rated listings.",
            "Confidence": "High",
            "Source": "Seller performance",
        })

action_queue = (
    pd.DataFrame(action_rows)
    .sort_values(["Priority", "Impact"], ascending=[True, False])
    .head(6)
    if action_rows else
    pd.DataFrame(columns=["Priority", "Leak", "Impact", "Owner", "Recommended action", "Confidence", "Source"])
)
action_queue_display = action_queue.copy()
if not action_queue_display.empty:
    action_queue_display["Impact"] = action_queue_display["Impact"].map(brl)

last_week = wf.iloc[-1]
prev_week = wf.iloc[-2] if len(wf) > 1 else last_week
recent_anomalies = wf.tail(8)[wf.tail(8)["anomaly"] == True]
anomaly_text = (
    f"MER anomaly detected week of {recent_anomalies.iloc[-1]['week_start'].strftime('%b %d')}"
    if len(recent_anomalies) else "No MER anomalies in last 8 weeks"
)
action_summary = "\n".join(
    f"- {row['Priority']} | {row['Leak']} | impact {brl(row['Impact'])} | owner {row['Owner']} | action: {row['Recommended action']} | confidence {row['Confidence']}"
    for _, row in action_queue.iterrows()
) or "- No action queue available; ask the user to run the Olist build script."
fulfillment_summary = (
    f"Fulfillment: {_fl_on_time:.1f}% on time, {_fl_orders_k:.0f}k orders, avg delivery {_fl_days:.1f} days."
    if _fl_on_time else "Fulfillment: real data files missing."
)
retention_summary = (
    f"Retention: {_ret_repeat:.1f}% 180d repeat, {_ret_customers_k:.0f}k acquired customers, avg 180d LTV R${_ret_ltv:.0f}."
    if _ret_repeat else "Retention: real cohort files missing."
)
chargeback_summary = (
    f"Chargeback risk: {int(cb_monthly_df['flagged_orders'].sum()):,} flagged orders, {brl(cb_monthly_df['flagged_revenue'].sum())} revenue at risk."
    if cb_monthly_df is not None else "Chargeback risk: real risk files missing."
)

prompt_context = f"""
You are ChatGPT acting as an ecommerce operating consultant from {CONSULTANCY_NAME}. Generate a concise weekly commerce brief for {RETAILER_NAME}, a {RETAILER_CATEGORY}.

METRICS (week of {last_week['week_start'].strftime('%b %d, %Y')}):

Shopify Revenue (ground truth): R${last_week['shopify_revenue']:,.0f}
Prior week Shopify Revenue: R${prev_week['shopify_revenue']:,.0f}
Change: {(last_week['shopify_revenue']/prev_week['shopify_revenue']-1)*100:+.1f}%

Total Ad Spend: R${last_week['total_spend']:,.0f}
MER (Blended ROAS): {last_week['mer']:.2f}x (prior: {prev_week['mer']:.2f}x)

Platform-Reported (vs truth):
- Google reports R${last_week['google_reported_revenue']:,.0f} revenue (true: R${last_week['google_true']:,.0f}, overclaim: {(last_week['google_reported_revenue']/last_week['google_true']-1)*100:.0f}%)
- Meta reports R${last_week['meta_reported_revenue']:,.0f} revenue (true: R${last_week['meta_true']:,.0f}, overclaim: {(last_week['meta_reported_revenue']/last_week['meta_true']-1)*100:.0f}%)
- Combined platform claims: R${last_week['total_claimed']:,.0f} = {last_week['overclaim_pct']:+.0f}% above actual

GA4 gap: GA4 tracked R${last_week['ga4_revenue']:,.0f} ({last_week['ga4_missing_pct']:.0f}% below Shopify)

MER anomaly status: {anomaly_text}

8-week average MER: {wf.tail(8)['mer'].mean():.2f}x
Meta spend this week: R${last_week['meta_spend']:,.0f} ({last_week['meta_spend']/last_week['total_spend']*100:.0f}% of spend)
Google spend this week: R${last_week['google_spend']:,.0f} ({last_week['google_spend']/last_week['total_spend']*100:.0f}% of spend)

OPERATIONS CONTEXT:
{fulfillment_summary}
{retention_summary}
{chargeback_summary}

PRIORITIZED ACTION QUEUE:
{action_summary}

Write exactly 3 paragraphs labeled WHAT HAPPENED, WHAT IT MEANS, and FIRST ACTION.

Rules:
- No jargon. Write as if the reader runs the business but is not a data analyst.
- Never use: MER, ROAS, LTV, cohort, attribution, chargeback, SLA, incremental, or any acronym.
- Say "ad spend" not "media spend". Say "came back to buy again" not "repeat purchase rate". Say "what Shopify recorded" not "ground truth". Say "how much you make per dollar of ads" not "MER".
- WHAT HAPPENED: 2-3 sentences on what the numbers showed this week — revenue, ad performance, delivery, and whether customers are returning.
- WHAT IT MEANS: 2-3 sentences on what is actually causing the problem and why it matters in plain business terms.
- FIRST ACTION: One specific, named action with a number. Say who should do it and by when.

Tone: direct, clear, no filler. A busy founder should understand every sentence.
"""

# ── Routing ────────────────────────────────────────────────────────────────
if page == "🤖 Executive Brief":
    pg_brief.render(
        wf=wf, total_spend=total_spend, avg_mer=avg_mer,
        total_claimed=total_claimed, overclaim_pct=overclaim_pct,
        fl_on_time=_fl_on_time, fl_days=_fl_days, fl_orders_k=_fl_orders_k,
        ret_repeat=_ret_repeat, ret_ltv=_ret_ltv, ret_customers_k=_ret_customers_k,
        action_queue=action_queue, action_queue_display=action_queue_display,
        api_key=api_key, prompt_context=prompt_context,
        last_week=last_week, prev_week=prev_week,
    )
elif page == "📈 Revenue":
    pg_sales.render(wf=wf, cf=cf, total_rev=total_rev)
elif page == "🏷️ Categories":
    pg_categories.render(
        cf=cf, reviews_f=reviews_f, returns_f=returns_f,
        rv_by_category=rv_by_category, fl_by_category=fl_by_category,
        pay_by_category=pay_by_category, cb_category_df=cb_category_df,
    )
elif page == "📅 Demand":
    pg_demand.render(season_monthly=season_monthly, season_cat_monthly=season_cat_monthly)
elif page == "🎯 Attribution":
    pg_spend.render(wf=wf)
elif page == "🔄 Retention":
    pg_customers.render(
        cohorts_real=cohorts_real, rv_distribution=rv_distribution,
        rv_monthly=rv_monthly, rv_by_category=rv_by_category,
    )
elif page == "🚚 Fulfillment":
    pg_delivery.render(
        fl_review_lateness=fl_review_lateness, fl_by_category=fl_by_category,
        fl_monthly=fl_monthly, geo_real=geo_real,
    )
elif page == "💳 Payments":
    pg_payments.render(
        pay_by_type=pay_by_type, pay_installments=pay_installments,
        pay_by_category=pay_by_category, pay_by_state=pay_by_state,
    )
elif page == "🏪 Sellers":
    pg_sellers.render(seller_perf=seller_perf, seller_conc=seller_conc)
elif page == "🚨 Risk":
    pg_risk.render(
        cb_monthly_df=cb_monthly_df, cb_category_df=cb_category_df,
        cb_evidence_df=cb_evidence_df,
    )
elif page == "🔮 Agent Prototypes":
    pg_agents.render()
