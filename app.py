"""
Commerce Leak Studio
Retail operating dashboard demo — synthetic attribution modeled on Olist Brazil
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import duckdb
from datetime import datetime

from pathlib import Path
from html import escape
from data_gen import load_all

CONSULTANCY_NAME = "Torm Data Co."
PRODUCT_NAME = "Commerce Leak Studio"
RETAILER_NAME = "Luma & Co."
RETAILER_CATEGORY = "Brazilian home, gifts, and lifestyle marketplace"
BRAND_PROMISE = "Find the profit leaks hiding between marketing, fulfillment, and retention."

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Commerce Leak Studio",
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

  /* Section headings — more vertical air */
  h3 { margin-top: 8px !important; margin-bottom: 12px !important; }

  /* Divider breathing room */
  [data-testid="stDivider"] { margin: 20px 0 !important; }

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
</style>
""", unsafe_allow_html=True)

# ── Plotly dark template ───────────────────────────────────────────────────
PLOT_THEME = dict(
    paper_bgcolor="#09090e",
    plot_bgcolor="#09090e",
    font=dict(color="#8888aa", size=11, family="JetBrains Mono, monospace"),
    xaxis=dict(gridcolor="#1c1c2a", zerolinecolor="#1c1c2a"),
    yaxis=dict(gridcolor="#1c1c2a", zerolinecolor="#1c1c2a"),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#9090b0")),
    margin=dict(l=48, r=24, t=36, b=36),
)


def plot_layout(**overrides):
    layout = PLOT_THEME.copy()
    for key, value in overrides.items():
        if isinstance(layout.get(key), dict) and isinstance(value, dict):
            merged = layout[key].copy()
            merged.update(value)
            layout[key] = merged
        else:
            layout[key] = value
    return layout


def brl(value):
    if value is None or pd.isna(value):
        return "—"
    value = float(value)
    if abs(value) >= 1_000_000:
        return f"R${value / 1_000_000:.1f}M"
    if abs(value) >= 1_000:
        return f"R${value / 1_000:.0f}k"
    return f"R${value:,.0f}"


def pct(value):
    if value is None or pd.isna(value):
        return "—"
    return f"{float(value):.1f}%"


def file_status(filename):
    p = Path("data") / filename
    if not p.exists():
        return "Missing"
    modified = datetime.fromtimestamp(p.stat().st_mtime).strftime("%b %d, %Y %H:%M")
    return f"Ready · {modified}"


DEMO_BRIEF = """WHAT HAPPENED: MER held above the recent baseline while the platforms still claimed more revenue than Shopify recorded. Fulfillment remains the clearest customer-experience leak: late orders are concentrated enough to show up in review quality, and 180-day repeat purchase is still too low to let paid acquisition compound.

WHAT IT MEANS: The growth team should not optimize from platform ROAS alone because the claimed revenue pool is inflated. The operating issue is broader than attribution: late delivery suppresses reviews, weak reviews reduce repeat purchase, and risky payment or chargeback segments create finance drag after the order is already won.

FIRST ACTION: Put the P1 queue into this week's operating meeting: use MER as the paid-spend guardrail, open an SLA recovery queue for late orders after day 3, and assign Retention a 45-day second-purchase flow with a target of moving 180-day repeat toward 5.0%."""


def render_brief_box(text, opacity=1.0, intro=None):
    intro_html = f"<em>{escape(intro)}</em>\n\n" if intro else ""
    return f'<div class="brief-box" style="opacity:{opacity}">{intro_html}{escape(text)}</div>'


def generate_openai_brief(api_key, prompt_context, brief_placeholder):
    if not api_key:
        brief_placeholder.markdown(
            """
<div class="callout callout-red">
No API key provided. Enter your OpenAI API key in the sidebar, or use demo mode below.
</div>
""",
            unsafe_allow_html=True,
        )
        brief_placeholder.markdown(render_brief_box(DEMO_BRIEF, 0.72, "Demo output shown while live AI is unavailable:"), unsafe_allow_html=True)
        return

    with st.spinner("Generating brief..."):
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            stream = client.responses.create(
                model="gpt-oss-20b",
                input=[
                    {
                        "role": "user",
                        "content": prompt_context,
                    }
                ],
                max_output_tokens=600,
                stream=True,
            )
            brief_text = ""
            for event in stream:
                if event.type == "response.output_text.delta":
                    brief_text += event.delta
                    brief_placeholder.markdown(
                        render_brief_box(f"{brief_text}▌"),
                        unsafe_allow_html=True,
                    )
                elif event.type == "error":
                    err = getattr(event, "error", None)
                    raise RuntimeError(getattr(err, "message", str(err)))
            brief_placeholder.markdown(render_brief_box(brief_text), unsafe_allow_html=True)
        except Exception as e:
            message = str(e)
            quota_like = any(token in message.lower() for token in ["quota", "rate limit", "insufficient_quota", "billing"])
            if quota_like:
                brief_placeholder.markdown(
                    """
<div class="callout callout-amber">
Live AI is unavailable because the OpenAI account is out of quota or rate-limited. Demo mode is shown below using the same dashboard context.
</div>
""",
                    unsafe_allow_html=True,
                )
                brief_placeholder.markdown(render_brief_box(DEMO_BRIEF, 0.78, "Quota-safe demo output:"), unsafe_allow_html=True)
            else:
                brief_placeholder.error(f"API error: {e}")


# Pillar palette — applied consistently to every chart in its tab group
COLORS = dict(
    # Platform channels
    shopify="#22d3a0",
    google="#3b9eff",
    meta="#ff6b6b",
    email="#f5c542",
    organic="#9b72cf",
    # Three pillars
    attribution="#7c6bff",   # indigo  — Attribution Lie + MER
    fulfillment="#22d3a0",   # emerald — Fulfillment + Geography
    retention="#f5c542",     # amber   — Cohorts + Reviews
    # Utility
    claimed="#ff5566",
    geo="#38bdf8",
    returns="#ff8a4c",
)

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
    page = st.sidebar.radio("Navigation", [
        "🤖 Executive Brief",
        "📊 Sales",
        "📅 Demand",
        "🟣 Spend",
        "🟡 Customers",
        "🟢 Delivery",
        "💳 Payments",
        "🏪 Sellers",
        "🚨 Risk",
    ])


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
        help="Optional. Live generation uses gpt-oss-20b; demo mode still works when quota is unavailable.",
    )
    st.caption("Live mode uses OpenAI's open-weight gpt-oss-20b model. Demo mode stays visible during quota issues.")

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
wf  = weekly[(weekly["week_start"] >= start_ts) & (weekly["week_start"] <= end_ts)].copy()
cf  = categories[(categories["week_start"] >= start_ts) & (categories["week_start"] <= end_ts)].copy()

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

# ── Action queue inputs ───────────────────────────────────────────────────
action_rows = []
phantom_revenue = max(total_claimed - total_rev, 0)
if phantom_revenue > 0:
    meta_true = wf["meta_true"].sum()
    google_true = wf["google_true"].sum()
    meta_overclaim = (wf["meta_reported_revenue"].sum() / meta_true - 1) * 100 if meta_true else 0
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
    late_revenue_proxy = late_orders * avg_order_value_real
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
    cohort_customers = cohorts_real["cohort_size"].sum()
    repeat_rate = (cohorts_real["ret_180d"] * cohorts_real["cohort_size"]).sum() / cohort_customers
    target_repeat = 0.05
    incremental_customers = max(target_repeat - repeat_rate, 0) * cohort_customers
    retention_upside = incremental_customers * cohorts_real["ltv_180d"].mean()
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
    cb_risk = cb_monthly_df["flagged_revenue"].sum()
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
    payment_impact = high_risk_payment["orders"] * high_risk_payment["avg_value"] * high_risk_payment["cancellation_rate"]
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

source_health = pd.DataFrame([
    {"Dataset": "Synthetic weekly", "Scope": f"{len(wf)} filtered weeks", "Status": "Ready · generated in app"},
    {"Dataset": "Fulfillment", "Scope": "Delivery SLA, category, monthly", "Status": file_status("fulfillment_monthly.csv")},
    {"Dataset": "Retention", "Scope": "Cohorts and 180d LTV", "Status": file_status("cohorts_real.csv")},
    {"Dataset": "Reviews", "Scope": "Score distribution, monthly, category", "Status": file_status("reviews_monthly.csv")},
    {"Dataset": "Payments", "Scope": "Payment type and installments", "Status": file_status("payments_by_type.csv")},
    {"Dataset": "Sellers", "Scope": "Seller quality and concentration", "Status": file_status("seller_performance.csv")},
    {"Dataset": "Chargeback risk", "Scope": "3-signal proxy model", "Status": file_status("chargeback_monthly.csv")},
    {"Dataset": "Seasonality", "Scope": "Monthly demand and category mix", "Status": file_status("seasonality_monthly.csv")},
])

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
    if _fl_on_time else
    "Fulfillment: real data files missing."
)
retention_summary = (
    f"Retention: {_ret_repeat:.1f}% 180d repeat, {_ret_customers_k:.0f}k acquired customers, avg 180d LTV R${_ret_ltv:.0f}."
    if _ret_repeat else
    "Retention: real cohort files missing."
)
chargeback_summary = (
    f"Chargeback risk: {int(cb_monthly_df['flagged_orders'].sum()):,} flagged orders, {brl(cb_monthly_df['flagged_revenue'].sum())} revenue at risk."
    if cb_monthly_df is not None else
    "Chargeback risk: real risk files missing."
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

Write exactly 3 paragraphs:
1. WHAT HAPPENED: 2-3 sentences on the key growth, attribution, fulfillment, retention, and risk numbers.
2. WHAT IT MEANS: 2-3 sentences connecting the biggest leaks to profit or customer experience.
3. FIRST ACTION: One specific owner-ready recommendation with a number attached.

Tone: direct, no fluff, treat the reader as smart. No bullet points. Plain prose.
"""


if page == "🤖 Executive Brief":
    # ── Homepage story ─────────────────────────────────────────────────────────
    p1_count = int((action_queue["Priority"] == "P1").sum()) if not action_queue.empty else 0
    late_context = f"{_fl_on_time:.1f}% on time" if _fl_on_time else "real data pending"
    repeat_context = f"{_ret_repeat:.1f}% repeat" if _ret_repeat else "real data pending"
    if action_queue.empty:
        top_leak = "Run the data build"
        top_owner = "Ops"
        top_impact = "Pending"
        top_action = "Generate the real-data files to populate the operating story."
    else:
        top_row = action_queue.iloc[0]
        top_leak = escape(str(top_row["Leak"]))
        top_owner = escape(str(top_row["Owner"]))
        top_impact = brl(top_row["Impact"])
        top_action = escape(str(top_row["Recommended action"]))

    st.markdown(f"""
    <div class="story-shell">
      <div class="story-header">
        <div>
          <p class="kpi-label" style="margin:0 0 6px">{RETAILER_NAME} operating story</p>
          <p class="story-title">Revenue is leaking after the click.</p>
          <p class="story-copy">The story is simple: paid demand looks productive, fulfillment decides the customer experience, and weak repeat purchase keeps acquisition from compounding.</p>
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
          <p class="story-line">{f'{_fl_orders_k:.0f}k orders, {_fl_days:.1f} day average delivery.' if _fl_on_time else 'Build Olist files for fulfillment coverage.'}</p>
        </div>
        <div class="story-arrow">→</div>
        <div class="story-beat" style="--beat-color:#f5c542">
          <p class="story-label">Repeat</p>
          <p class="story-number">{repeat_context}</p>
          <p class="story-line">{f'{_ret_customers_k:.0f}k customers, R${_ret_ltv:.0f} average 180d LTV.' if _ret_repeat else 'Build Olist files for cohort coverage.'}</p>
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

    ai_status = "Live key provided" if api_key else "Demo mode"
    cta_left, cta_right = st.columns([0.26, 0.74])
    with cta_left:
        top_generate_btn = st.button("Generate client brief", type="primary", use_container_width=True, key="top_ai_generate")
    with cta_right:
        st.caption(f"AI Brief Studio · {ai_status} · live model gpt-oss-20b · demo fallback remains available")
    top_brief_placeholder = st.empty()
    if top_generate_btn:
        generate_openai_brief(api_key, prompt_context, top_brief_placeholder)

    st.markdown("### Action Queue")
    if action_queue_display.empty:
        st.info("Run `python scripts/build_olist_data.py` to populate the operating queue.", icon="⚙️")
    else:
        cards_html = "<div style='display: flex; flex-direction: column; gap: 12px; margin-bottom: 24px;'>"
        for _, row in action_queue_display.head(6).iterrows():
            owner = row["Owner"]
            color = "#7c6bff" # default attribution (Acquisition)
            if "Ops" in owner: color = "#22d3a0" # Fulfillment
            elif "Retention" in owner: color = "#f5c542" # Repeat
            elif "Finance" in owner: color = "#ff5566" # Risk
            
            cards_html += f"""
            <div style='background: #0f0f18; border-left: 4px solid {color}; border-radius: 8px; padding: 16px; border-top: 1px solid #1c1c2a; border-right: 1px solid #1c1c2a; border-bottom: 1px solid #1c1c2a;'>
                <div style='display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;'>
                    <div>
                        <span style='color: {color}; font-family: monospace; font-size: 11px; font-weight: bold; padding: 2px 6px; background: {color}20; border-radius: 4px; margin-right: 8px;'>{row['Priority']}</span>
                        <strong style='color: #eeeeff; font-size: 16px;'>{escape(str(row['Leak']))}</strong>
                    </div>
                    <div style='text-align: right;'>
                        <span style='color: #a0a0c0; font-size: 12px; margin-right: 12px;'>Impact:</span>
                        <strong style='color: #eeeeff; font-size: 16px;'>{row['Impact']}</strong>
                    </div>
                </div>
                <div style='color: #8d8daf; font-size: 14px; line-height: 1.5; margin-bottom: 12px;'>
                    {escape(str(row['Recommended action']))}
                </div>
                <div style='display: flex; gap: 16px; font-size: 11px; color: #6060a0; font-family: monospace; text-transform: uppercase;'>
                    <span>Owner: <strong style='color: #a0a0c0;'>{escape(str(row['Owner']))}</strong></span>
                    <span>Confidence: <strong style='color: #a0a0c0;'>{escape(str(row['Confidence']))}</strong></span>
                    <span>Source: <strong style='color: #a0a0c0;'>{escape(str(row['Source']))}</strong></span>
                </div>
            </div>
            """
        cards_html += "</div>"
        st.markdown(cards_html, unsafe_allow_html=True)
        
    with st.expander("Source coverage details"):
        st.markdown(
            "Synthetic attribution is used where Olist has no channel data. Operational tabs use pre-aggregated Olist files from `scripts/build_olist_data.py`."
        )
        st.dataframe(source_health, use_container_width=True, hide_index=True)

    st.divider()



# ═══════════════════════════════════════════════════════════════════════════
# SEASONALITY
# ═══════════════════════════════════════════════════════════════════════════
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

if page == "📅 Demand":
    st.markdown("### Seasonal demand patterns")
    st.markdown(
        '<p class="kpi-label">Real Olist dataset · Sep 2016 – Oct 2018 · delivered orders</p>',
        unsafe_allow_html=True,
    )

    if season_monthly is None:
        st.warning("Run `python scripts/build_olist_data.py` first.", icon="⚙️")
    else:
        sm = season_monthly.copy()
        sm["month_name"] = sm["month_num"].apply(lambda m: MONTH_NAMES[m - 1])

        # ── KPIs ──────────────────────────────────────────────────────────
        peak_row   = sm.loc[sm["orders"].idxmax()]
        trough_row = sm.loc[sm["orders"].idxmin()]
        peak_ratio = peak_row["orders"] / trough_row["orders"]

        # YoY: compare the months both 2017 and 2018 share
        y17 = sm[sm["year"] == 2017].set_index("month_num")["orders"]
        y18 = sm[sm["year"] == 2018].set_index("month_num")["orders"]
        shared = y17.index.intersection(y18.index)
        yoy_growth = (y18[shared].sum() / y17[shared].sum() - 1) * 100 if len(shared) else 0

        sn1, sn2, sn3, sn4 = st.columns(4)
        sn1.metric("Peak Month",    peak_row["purchase_month"],
                   f"{peak_row['orders']:,} orders")
        sn2.metric("Trough Month",  trough_row["purchase_month"],
                   f"{trough_row['orders']:,} orders")
        sn3.metric("Peak / Trough", f"{peak_ratio:.1f}×",
                   "seasonal amplitude")
        sn4.metric("YoY Growth (shared months)", f"{yoy_growth:+.1f}%",
                   "2018 vs 2017")

        st.divider()

        # ── Trend decomposition ───────────────────────────────────────────
        # Centered 3-month rolling mean as trend
        sm = sm.sort_values("purchase_month").reset_index(drop=True)
        sm["trend"]     = sm["orders"].rolling(3, center=True, min_periods=2).mean()
        sm["detrended"] = sm["orders"] - sm["trend"]

        fig_trend = go.Figure()
        fig_trend.add_trace(go.Bar(
            x=sm["purchase_month"], y=sm["orders"],
            name="Monthly orders",
            marker_color="rgba(59,158,255,0.4)",
        ))
        fig_trend.add_trace(go.Scatter(
            x=sm["purchase_month"], y=sm["trend"],
            name="Trend (3-mo avg)",
            mode="lines",
            line=dict(color="#3b9eff", width=2.5),
        ))
        # Annotate peak
        fig_trend.add_annotation(
            x=peak_row["purchase_month"], y=peak_row["orders"],
            text=f"Peak: {int(peak_row['orders']):,}",
            showarrow=True, arrowhead=2,
            font=dict(color="#f5c542", size=10),
            bgcolor="rgba(0,0,0,0.5)",
            arrowcolor="#f5c542",
            ay=-30,
        )
        fig_trend.update_layout(**plot_layout(
            title="Monthly Orders with Trend Decomposition",
            height=320,
            yaxis=dict(title="Orders"),
            legend=dict(orientation="h", y=1.15),
        ))
        st.plotly_chart(fig_trend, use_container_width=True)

        # ── Seasonal index + YoY ──────────────────────────────────────────
        col_s1, col_s2 = st.columns(2)

        with col_s1:
            # Seasonal index: avg orders per calendar month / overall monthly avg
            month_avg = sm.groupby("month_num")["orders"].mean()
            overall_avg = sm["orders"].mean()
            indices = (month_avg / overall_avg * 100).reset_index()
            indices.columns = ["month_num", "index"]
            indices["month_name"] = indices["month_num"].apply(lambda m: MONTH_NAMES[m - 1])
            indices["color"] = indices["index"].apply(
                lambda v: "#f5c542" if v >= 100 else "#3b9eff"
            )

            fig_idx = go.Figure(go.Bar(
                x=indices["month_name"],
                y=indices["index"],
                marker_color=indices["color"],
                text=indices["index"].map(lambda v: f"{v:.0f}"),
                textposition="outside",
                hovertemplate="%{x}<br>Seasonal index: %{y:.1f}<extra></extra>",
            ))
            fig_idx.add_hline(y=100, line_dash="dot", line_color="#2a2a40",
                              annotation_text="baseline 100",
                              annotation_font_color="#5a5a78",
                              annotation_position="right")
            fig_idx.update_layout(**plot_layout(
                title="Seasonal Index by Month  (100 = average)",
                height=300,
                yaxis=dict(title="Index", range=[50, 160]),
                xaxis=dict(title=""),
            ))
            st.plotly_chart(fig_idx, use_container_width=True)

        with col_s2:
            # Year-over-year overlay
            YEAR_COLORS = {2016: "#9b72cf", 2017: "#3b9eff", 2018: "#22d3a0"}
            fig_yoy = go.Figure()
            for yr, grp in sm.groupby("year"):
                grp = grp.sort_values("month_num")
                fig_yoy.add_trace(go.Scatter(
                    x=grp["month_name"],
                    y=grp["orders"],
                    name=str(yr),
                    mode="lines+markers",
                    line=dict(color=YEAR_COLORS.get(yr, "#888899"), width=2),
                    marker=dict(size=5),
                    opacity=0.5 if yr == 2016 else 1.0,
                ))
            fig_yoy.update_layout(**plot_layout(
                title="Year-over-Year Orders  (2016 partial)",
                height=300,
                xaxis=dict(title="Month", categoryorder="array",
                           categoryarray=MONTH_NAMES),
                yaxis=dict(title="Orders"),
                legend=dict(orientation="h", y=1.15),
            ))
            st.plotly_chart(fig_yoy, use_container_width=True)

        # ── Category mix ─────────────────────────────────────────────────
        if season_cat_monthly is not None:
            scm = season_cat_monthly.copy()
            top5 = scm.groupby("primary_category")["orders"].sum().nlargest(5).index
            scm  = scm[scm["primary_category"].isin(top5)]
            CAT_COLORS = ["#7c6bff", "#22d3a0", "#f5c542", "#3b9eff", "#ff8a4c"]

            fig_catmix = go.Figure()
            for i, cat in enumerate(top5):
                sub = scm[scm["primary_category"] == cat].sort_values("purchase_month")
                fig_catmix.add_trace(go.Bar(
                    x=sub["purchase_month"],
                    y=sub["orders"],
                    name=cat,
                    marker_color=CAT_COLORS[i % len(CAT_COLORS)],
                ))
            fig_catmix.update_layout(**plot_layout(
                barmode="stack",
                title="Which categories drive demand each month  —  top 5",
                height=280,
                legend=dict(orientation="h", y=1.15, font=dict(size=10)),
                yaxis=dict(title="Orders"),
            ))
            st.plotly_chart(fig_catmix, use_container_width=True)

        st.markdown("""
<div class="callout">
<strong>Reading this:</strong> The seasonal index shows which months historically over- or under-perform
the annual average — useful for planning spend allocation before peak periods.
The year-over-year chart shows whether last year's pattern is repeating this year.
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# SALES
# ═══════════════════════════════════════════════════════════════════════════
if page == "📊 Sales":
    st.markdown("### Sales overview")

    s_k1, s_k2, s_k3, s_k4 = st.columns(4)
    total_orders  = int(wf["shopify_orders"].sum())
    avg_aov       = total_rev / total_orders if total_orders else 0
    first_4 = wf.head(4)["shopify_revenue"].sum()
    last_4  = wf.tail(4)["shopify_revenue"].sum()
    recent_growth = (last_4 / first_4 - 1) * 100 if first_4 else 0
    top_category  = cf.groupby("category")["revenue"].sum().idxmax()

    s_k1.metric("Revenue",           f"R${total_rev/1e6:.1f}M")
    s_k2.metric("Orders",            f"{total_orders:,}")
    s_k3.metric("AOV",               f"R${avg_aov:.0f}")
    s_k4.metric("Recent vs Start",   f"{recent_growth:+.0f}%")

    col_s1, col_s2 = st.columns([3, 2])

    with col_s1:
        fig_sales = go.Figure()
        fig_sales.add_trace(go.Scatter(
            x=wf["week_start"], y=wf["shopify_revenue"],
            name="Revenue", mode="lines+markers",
            line=dict(color=COLORS["shopify"], width=2),
            marker=dict(size=3),
            fill="tozeroy",
            fillcolor="rgba(34,211,160,0.08)",
        ))
        fig_sales.add_trace(go.Bar(
            x=wf["week_start"], y=wf["shopify_orders"],
            name="Orders", marker_color="rgba(59,158,255,0.28)",
            yaxis="y2",
        ))
        fig_sales.update_layout(**plot_layout(
            title="Weekly Revenue and Orders",
            height=360,
            legend=dict(orientation="h", y=1.13),
            yaxis=dict(title="Revenue (BRL)", gridcolor="#1c1c2a"),
            yaxis2=dict(title="Orders", overlaying="y", side="right", showgrid=False),
        ))
        st.plotly_chart(fig_sales, use_container_width=True)

    with col_s2:
        category_sales = (
            cf.groupby("category", as_index=False)
            .agg(revenue=("revenue", "sum"))
            .sort_values("revenue", ascending=False)
            .head(7)
        )
        fig_mix = go.Figure(go.Pie(
            labels=category_sales["category"].str.replace("_", " ").str.title(),
            values=category_sales["revenue"],
            hole=0.55,
            marker=dict(colors=["#22d3a0", "#3b9eff", "#7c6bff", "#f5c542",
                                 "#9b72cf", "#38bdf8", "#ff8a4c"]),
        ))
        fig_mix.update_layout(**plot_layout(
            title="Revenue Mix by Category",
            height=360,
            showlegend=True,
            legend=dict(orientation="h", y=-0.05, font=dict(size=10)),
        ))
        st.plotly_chart(fig_mix, use_container_width=True)

    best_week = wf.loc[wf["shopify_revenue"].idxmax()]
    st.markdown(f"""
<div class="callout">
Peak week: <strong>{best_week['week_start'].strftime('%b %d, %Y')}</strong> —
<strong>R${best_week['shopify_revenue']:,.0f}</strong> revenue,
<strong>{int(best_week['shopify_orders']):,}</strong> orders.
Top category: <strong>{top_category.replace('_', ' ').title()}</strong>.
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# ATTRIBUTION  (indigo)
# ═══════════════════════════════════════════════════════════════════════════
if page == "🟣 Spend":
    # ── Section 1: The Lie ─────────────────────────────────────────────────
    st.markdown(
        '<p style="color:#7c6bff;font-size:10px;letter-spacing:.15em;'
        'text-transform:uppercase;font-family:monospace;margin:0 0 4px">Attribution</p>',
        unsafe_allow_html=True,
    )
    st.markdown("### What platforms claim vs what actually happened")

    st.markdown("""
<div class="callout callout-red">
<strong>The impossible math:</strong> Meta, Google, and Email each claim the same customer journey.
Sum their reported revenue and you get <strong>~140% of actual Shopify revenue</strong>.
One sale. Three winners.
</div>
""", unsafe_allow_html=True)

    fig_lie = go.Figure()
    fig_lie.add_trace(go.Bar(
        x=wf["week_start"], y=wf["shopify_revenue"],
        name="Shopify (truth)", marker_color=COLORS["shopify"], opacity=0.9,
    ))
    fig_lie.add_trace(go.Scatter(
        x=wf["week_start"], y=wf["total_claimed"],
        name="Total claimed by platforms", mode="lines",
        line=dict(color=COLORS["claimed"], width=2, dash="dot"),
    ))
    fig_lie.update_layout(**plot_layout(
        title="Weekly Revenue: Shopify Truth vs Platform Claims",
        barmode="overlay", height=320,
        legend=dict(orientation="h", y=1.15),
    ))
    st.plotly_chart(fig_lie, use_container_width=True)

    # ROAS cards
    st.markdown("#### Platform ROAS: Reported vs True")
    col_a, col_b, col_c = st.columns(3)

    avg_google_rep  = (wf["google_reported_revenue"] / wf["google_spend"]).mean()
    avg_meta_rep    = (wf["meta_reported_revenue"]   / wf["meta_spend"]).mean()
    avg_google_true = (wf["google_true"] / wf["google_spend"]).mean()
    avg_meta_true   = (wf["meta_true"]   / wf["meta_spend"]).mean()

    with col_a:
        st.markdown("""
<div style="background:#0f0f18;border:1px solid #1c1c2a;border-radius:10px;padding:16px">
<p class="kpi-label">Google Ads</p>
<p style="font-size:28px;font-weight:800;color:#3b9eff;margin:4px 0">
  {:.1f}x <span style="font-size:14px;color:#444466">reported</span>
</p>
<p style="font-size:22px;font-weight:600;color:#22d3a0">
  {:.1f}x <span style="font-size:12px;color:#444466">true</span>
</p>
<p style="font-size:11px;color:#5a5a78;margin-top:6px">
  ~{:.0f}% overclaim — PMax + DDA cross-channel double-counting
</p>
</div>
""".format(avg_google_rep, avg_google_true, (avg_google_rep/avg_google_true - 1)*100),
        unsafe_allow_html=True)

    with col_b:
        st.markdown("""
<div style="background:#0f0f18;border:1px solid #1c1c2a;border-radius:10px;padding:16px">
<p class="kpi-label">Meta Ads</p>
<p style="font-size:28px;font-weight:800;color:#ff6b6b;margin:4px 0">
  {:.1f}x <span style="font-size:14px;color:#444466">reported</span>
</p>
<p style="font-size:22px;font-weight:600;color:#22d3a0">
  {:.1f}x <span style="font-size:12px;color:#444466">true</span>
</p>
<p style="font-size:11px;color:#5a5a78;margin-top:6px">
  ~{:.0f}% overclaim — 7-day click / 1-day view + Advantage+ opacity
</p>
</div>
""".format(avg_meta_rep, avg_meta_true, (avg_meta_rep/avg_meta_true - 1)*100),
        unsafe_allow_html=True)

    with col_c:
        avg_claimed_weekly = wf["total_claimed"].mean()
        avg_shopify_weekly = wf["shopify_revenue"].mean()
        avg_overclaim      = wf["overclaim_pct"].mean()
        st.markdown("""
<div style="background:#200a10;border:1px solid #ff556630;border-radius:10px;padding:16px">
<p class="kpi-label" style="color:#ff5566">Combined Overclaim</p>
<p style="font-size:28px;font-weight:800;color:#ff5566;margin:4px 0">
  +{:.0f}%
</p>
<p style="font-size:13px;color:#d0a0a8">
  R${:,.0f} claimed vs R${:,.0f} actual per week
</p>
<p style="font-size:11px;color:#804040;margin-top:6px">
  R${:,.0f} in phantom revenue over this period
</p>
</div>
""".format(avg_overclaim, avg_claimed_weekly, avg_shopify_weekly,
           wf["total_claimed"].sum() - wf["shopify_revenue"].sum()),
        unsafe_allow_html=True)

    # ── Section 2: MER ────────────────────────────────────────────────────
    st.markdown('<div class="pillar-section"></div>', unsafe_allow_html=True)
    st.markdown("### Revenue per R$1 of ad spend — the one number that doesn't lie")
    st.markdown("""
<div class="callout" style="border-left-color:#7c6bff">
<strong>Media Efficiency Ratio</strong> = Total Shopify Revenue ÷ Total Ad Spend.
No attribution models, no platform self-reporting. Track this weekly and watch it move
as you change channel mix.
</div>
""", unsafe_allow_html=True)

    wf["mer_baseline"] = wf["mer"].rolling(8, min_periods=4).mean()
    wf["mer_std"]      = wf["mer"].rolling(8, min_periods=4).std()
    wf["mer_upper"]    = wf["mer_baseline"] + 1.5 * wf["mer_std"]
    wf["mer_lower"]    = wf["mer_baseline"] - 1.5 * wf["mer_std"]
    wf["anomaly"]      = (wf["mer"] < wf["mer_lower"]) | (wf["mer"] > wf["mer_upper"])

    col_m1, col_m2 = st.columns([3, 2])

    with col_m1:
        fig_mer = go.Figure()
        fig_mer.add_trace(go.Scatter(
            x=pd.concat([wf["week_start"], wf["week_start"][::-1]]),
            y=pd.concat([wf["mer_upper"], wf["mer_lower"][::-1]]),
            fill="toself", fillcolor="rgba(124,107,255,0.07)",
            line=dict(color="rgba(0,0,0,0)"),
            name="Normal range",
        ))
        fig_mer.add_trace(go.Scatter(
            x=wf["week_start"], y=wf["mer_baseline"],
            name="8-wk baseline", line=dict(color="#444466", width=1.5, dash="dot"),
        ))
        fig_mer.add_trace(go.Scatter(
            x=wf["week_start"], y=wf["mer"],
            name="MER", mode="lines+markers",
            line=dict(color=COLORS["attribution"], width=2),
            marker=dict(size=3),
        ))
        anoms = wf[wf["anomaly"] & wf["mer_baseline"].notna()]
        if len(anoms):
            fig_mer.add_trace(go.Scatter(
                x=anoms["week_start"], y=anoms["mer"],
                name="Anomaly", mode="markers",
                marker=dict(color="#ff5566", size=9, symbol="circle-open",
                            line=dict(width=2)),
            ))
        for _, row in wf[wf["season_label"] != ""].iterrows():
            fig_mer.add_annotation(
                x=row["week_start"], y=row["mer"] + 0.05,
                text=row["season_label"], showarrow=False,
                font=dict(size=8, color="#666699"), bgcolor="rgba(0,0,0,0.3)",
            )
        fig_mer.update_layout(**plot_layout(
            title="Weekly MER with Anomaly Detection",
            height=340, legend=dict(orientation="h", y=1.12),
            yaxis=dict(title="MER (Revenue / Spend)"),
        ))
        st.plotly_chart(fig_mer, use_container_width=True)

    with col_m2:
        fig_spend = go.Figure()
        for ch, col_name, name in [
            ("google_spend", COLORS["google"], "Google"),
            ("meta_spend",   COLORS["meta"],   "Meta"),
            ("email_cost",   COLORS["email"],  "Email"),
        ]:
            fig_spend.add_trace(go.Bar(
                x=wf["week_start"], y=wf[ch],
                name=name, marker_color=col_name, opacity=0.8,
            ))
        fig_spend.update_layout(**plot_layout(
            barmode="stack",
            title="Spend Mix by Channel",
            height=340, legend=dict(orientation="h", y=1.15),
            yaxis=dict(title="BRL"),
        ))
        st.plotly_chart(fig_spend, use_container_width=True)

    # ── Section 3: GA4 gap ────────────────────────────────────────────────
    st.markdown('<div class="pillar-section"></div>', unsafe_allow_html=True)
    st.markdown("### The GA4 gap — why analytics don't match your bank account")

    col_ga1, col_ga2 = st.columns([3, 2])

    with col_ga1:
        fig_ga4 = go.Figure()
        fig_ga4.add_trace(go.Scatter(
            x=wf["week_start"], y=wf["shopify_revenue"],
            name="Shopify (truth)", fill="tozeroy",
            line=dict(color=COLORS["shopify"], width=2),
            fillcolor="rgba(34,211,160,0.08)",
        ))
        fig_ga4.add_trace(go.Scatter(
            x=wf["week_start"], y=wf["ga4_revenue"],
            name="GA4 (broken client-side)", fill="tozeroy",
            line=dict(color="#888899", width=1.5, dash="dash"),
            fillcolor="rgba(136,136,153,0.06)",
        ))
        fig_ga4.update_layout(**plot_layout(
            title="Shopify Revenue vs GA4 Tracked Revenue",
            height=280, legend=dict(orientation="h", y=1.15),
        ))
        st.plotly_chart(fig_ga4, use_container_width=True)

    with col_ga2:
        st.markdown("""
<div class="callout" style="margin-top:32px">
<strong>Why the gap exists:</strong><br><br>
• <strong>Ad blockers</strong>: 25–35% of desktop users block GA4<br><br>
• <strong>iOS ITP</strong>: Safari caps first-party cookies at 7 days<br><br>
• <strong>Payment redirects</strong>: Stripe/PayPal kills the thank_you event<br><br>
• <strong>Shopify Checkout</strong>: GTM restricted in new checkout<br><br>
<strong>Fix:</strong> Server-side tracking via GTM Server Container + Meta CAPI
+ Google Enhanced Conversions
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# FULFILLMENT  (emerald)
# ═══════════════════════════════════════════════════════════════════════════
if page == "🟢 Delivery":
    # ── Section 1: Delivery SLA ────────────────────────────────────────────
    st.markdown(
        '<p style="color:#22d3a0;font-size:10px;letter-spacing:.15em;'
        'text-transform:uppercase;font-family:monospace;margin:0 0 4px">Fulfillment</p>',
        unsafe_allow_html=True,
    )
    st.markdown("### Delivery performance")
    st.markdown(
        '<p class="kpi-label">Real Olist dataset · 96k delivered orders · Sep 2016 – Oct 2018</p>',
        unsafe_allow_html=True,
    )

    if fl_review_lateness is None:
        st.warning("Run `python scripts/build_olist_data.py` first.", icon="⚙️")
    else:
        w_wt = fl_monthly["orders"]
        on_time_overall    = np.average(fl_monthly["on_time_rate"],      weights=w_wt)
        avg_days_overall   = np.average(fl_monthly["avg_delivery_days"], weights=w_wt)
        avg_review_overall = np.average(fl_monthly["avg_review_score"],  weights=w_wt)
        on_time_orders     = fl_by_category["orders"].sum()

        fk1, fk2, fk3, fk4 = st.columns(4)
        fk1.metric("On-Time Rate",     f"{on_time_overall*100:.1f}%")
        fk2.metric("Avg Delivery",     f"{avg_days_overall:.1f} days")
        fk3.metric("Avg Review Score", f"{avg_review_overall:.2f} / 5")
        fk4.metric("Orders analysed",  f"{on_time_orders:,.0f}")

        st.divider()
        col_f1, col_f2 = st.columns([3, 2])

        with col_f1:
            BUCKET_COLORS = ["#22d3a0", "#f5c542", "#ff8a4c", "#ff6b6b", "#ff2244"]
            fig_lateness = go.Figure(go.Bar(
                x=fl_review_lateness["bucket"],
                y=fl_review_lateness["avg_score"],
                marker_color=BUCKET_COLORS,
                text=fl_review_lateness["avg_score"].map(lambda v: f"{v:.2f}★"),
                textposition="outside",
                customdata=fl_review_lateness["order_count"],
                hovertemplate=(
                    "<b>%{x}</b><br>Avg score: %{y:.2f}<br>"
                    "Orders: %{customdata:,}<extra></extra>"
                ),
            ))
            fig_lateness.update_layout(**plot_layout(
                title="Review Score vs Delivery Lateness",
                height=360,
                yaxis=dict(title="Avg review score", range=[1, 5.5]),
                xaxis=dict(title=""),
            ))
            st.plotly_chart(fig_lateness, use_container_width=True)
            st.markdown("""
<div class="callout callout-red">
<strong>Key insight:</strong> On-time orders average <strong>4.4★</strong>.
Orders 8–14 days late drop to <strong>~2.0★</strong>.
Every late delivery is a review bomb — and reviews directly drive repeat purchase.
Fulfillment SLA is a direct LTV lever.
</div>
""", unsafe_allow_html=True)

        with col_f2:
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(
                x=fl_monthly["purchase_month"],
                y=fl_monthly["on_time_rate"] * 100,
                name="On-time %",
                mode="lines+markers",
                line=dict(color=COLORS["fulfillment"], width=2),
                marker=dict(size=4),
            ))
            fig_trend.add_trace(go.Scatter(
                x=fl_monthly["purchase_month"],
                y=fl_monthly["avg_delivery_days"],
                name="Avg days",
                mode="lines",
                line=dict(color=COLORS["geo"], width=2, dash="dot"),
                yaxis="y2",
            ))
            fig_trend.update_layout(**plot_layout(
                title="On-Time Rate & Delivery Speed",
                height=340,
                xaxis=dict(title="", tickangle=-45, nticks=8),
                yaxis=dict(title="On-time %", range=[70, 100]),
                yaxis2=dict(
                    title="Avg days", overlaying="y", side="right",
                    showgrid=False, range=[0, 40],
                ),
                legend=dict(orientation="h", y=1.18),
            ))
            st.plotly_chart(fig_trend, use_container_width=True)
            st.markdown("""
<div class="callout callout-green">
Avg delivery improved from ~15 days in late 2016 to ~9 days by mid-2018
as the seller network matured — tracking the review score improvement directly.
</div>
""", unsafe_allow_html=True)

    # ── Section 2: Geography ──────────────────────────────────────────────
    st.markdown('<div class="pillar-section"></div>', unsafe_allow_html=True)
    st.markdown("### Geographic demand & delivery coverage")
    st.markdown(
        '<p class="kpi-label">Real Olist dataset · customer delivery by Brazilian state</p>',
        unsafe_allow_html=True,
    )

    if geo_real is None:
        st.warning("Run `python scripts/build_olist_data.py` first.", icon="⚙️")
    else:
        top_state  = geo_real.loc[geo_real["revenue"].idxmax()]
        slow_state = geo_real.loc[geo_real["avg_delivery_days"].idxmax()]
        late_state = geo_real.loc[(1 - geo_real["on_time_rate"]).idxmax()]
        seller_gap = geo_real.loc[
            (geo_real["customers"] / geo_real["seller_count"].clip(lower=1)).idxmax()
        ]

        gk1, gk2, gk3, gk4 = st.columns(4)
        gk1.metric("Top State by Revenue",     top_state["state"],
                   f"R${top_state['revenue']/1e6:.1f}M")
        gk2.metric("Slowest Delivery",         slow_state["state"],
                   f"{slow_state['avg_delivery_days']:.1f} days avg", delta_color="inverse")
        gk3.metric("Highest Late Rate",        late_state["state"],
                   f"{(1-late_state['on_time_rate'])*100:.1f}% late", delta_color="inverse")
        gk4.metric("Worst Buyer/Seller Ratio", seller_gap["state"],
                   f"{int(seller_gap['customers'])} buyers / {int(seller_gap['seller_count'])} sellers")

        st.divider()
        col_g1, col_g2 = st.columns([3, 2])

        with col_g1:
            geo_plot = geo_real.dropna(subset=["lat", "lon"])
            log_rev  = np.log1p(geo_plot["revenue"])
            sizes    = (log_rev - log_rev.min()) / (log_rev.max() - log_rev.min()) * 36 + 10

            fig_map = go.Figure(go.Scattergeo(
                lon=geo_plot["lon"],
                lat=geo_plot["lat"],
                mode="markers",
                customdata=np.stack([
                    geo_plot["state"],
                    geo_plot["revenue"],
                    geo_plot["orders"],
                    geo_plot["avg_delivery_days"],
                    geo_plot["on_time_rate"] * 100,
                    geo_plot["avg_review_score"],
                    geo_plot["region"],
                ], axis=1),
                hovertemplate=(
                    "<b>%{customdata[0]}</b>  ·  %{customdata[6]}<br>"
                    "Revenue: R$%{customdata[1]:,.0f}<br>"
                    "Orders: %{customdata[2]:,.0f}<br>"
                    "Avg delivery: %{customdata[3]:.1f} days<br>"
                    "On-time: %{customdata[4]:.1f}%<br>"
                    "Review: %{customdata[5]:.2f}★"
                    "<extra></extra>"
                ),
                marker=dict(
                    size=sizes,
                    color=(1 - geo_plot["on_time_rate"]) * 100,
                    colorscale="RdYlGn_r",
                    cmin=0, cmax=30,
                    colorbar=dict(title="Late %", thickness=10, len=0.6),
                    line=dict(color="#09090e", width=1),
                    opacity=0.88,
                ),
            ))
            fig_map.update_layout(**plot_layout(
                title="Revenue by State  ·  colour = late delivery rate",
                height=460,
                geo=dict(
                    scope="south america",
                    projection_type="mercator",
                    center=dict(lat=-14, lon=-52),
                    lataxis_range=[-35, 6],
                    lonaxis_range=[-75, -32],
                    bgcolor="#09090e",
                    landcolor="#12122a",
                    countrycolor="#2a2a40",
                    coastlinecolor="#2a2a40",
                    showland=True, showcountries=True, showcoastlines=True,
                ),
            ))
            st.plotly_chart(fig_map, use_container_width=True)

        with col_g2:
            geo_sorted = geo_real.sort_values("avg_delivery_days", ascending=False).head(15)
            fig_days = go.Figure(go.Bar(
                x=geo_sorted["avg_delivery_days"],
                y=geo_sorted["state"],
                orientation="h",
                marker_color=geo_sorted["avg_delivery_days"].map(
                    lambda v: "#ff6b6b" if v > 20 else ("#f5c542" if v > 12 else "#22d3a0")
                ),
                text=geo_sorted["avg_delivery_days"].map(lambda v: f"{v:.1f}d"),
                textposition="auto",
            ))
            fig_days.update_layout(**plot_layout(
                title="Avg Delivery Days by State",
                height=460,
                xaxis=dict(title="Days"),
                yaxis=dict(title=""),
            ))
            st.plotly_chart(fig_days, use_container_width=True)

        st.markdown("""
<div class="callout callout-green">
<strong>Pattern:</strong> Northern and Northeastern states (AM, RR, AC, AP) have the longest delivery times
and lowest review scores — and the fewest sellers relative to buyer demand.
<strong>PA has 922 buyers per seller</strong>, the most underserved market in the dataset.
These regions are the clearest opportunity for localised fulfilment investment.
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# RETENTION  (amber)
# ═══════════════════════════════════════════════════════════════════════════
if page == "🟡 Customers":
    # ── Section 1: Cohorts ────────────────────────────────────────────────
    st.markdown(
        '<p style="color:#f5c542;font-size:10px;letter-spacing:.15em;'
        'text-transform:uppercase;font-family:monospace;margin:0 0 4px">Retention</p>',
        unsafe_allow_html=True,
    )
    st.markdown("### Cohort retention & LTV")
    st.markdown(
        '<p class="kpi-label">Real Olist dataset · 96k customers · true repeat-purchase retention</p>',
        unsafe_allow_html=True,
    )

    if cohorts_real is None:
        st.warning("Run `python scripts/build_olist_data.py` first.", icon="⚙️")
    else:
        overall_repeat  = (cohorts_real["ret_180d"] * cohorts_real["cohort_size"]).sum() / cohorts_real["cohort_size"].sum()
        avg_ltv_180     = cohorts_real["ltv_180d"].mean()
        total_customers = int(cohorts_real["cohort_size"].sum())
        n_outliers      = int(cohorts_real["is_outlier"].sum())

        ck1, ck2, ck3, ck4 = st.columns(4)
        ck1.metric("Total Acquired",   f"{total_customers:,}")
        ck2.metric("180d Repeat Rate", f"{overall_repeat*100:.1f}%", delta_color="inverse")
        ck3.metric("Avg LTV (180d)",   f"R${avg_ltv_180:.0f}")
        ck4.metric("Low-Retention Cohorts", str(n_outliers),
                   "flagged outliers", delta_color="inverse")

        st.markdown("""
<div class="callout callout-amber">
<strong>The retention problem:</strong> Only <strong>2.1% of customers</strong> placed a second
order within 180 days. Acquisition is not compounding into repeat revenue.
LTV grows almost entirely from first-order value, not from loyalty.
This makes CAC payback entirely dependent on first-order margin.
</div>
""", unsafe_allow_html=True)

        col_c1, col_c2 = st.columns([3, 2])

        with col_c1:
            hm = cohorts_real[["cohort_month", "ret_30d", "ret_60d", "ret_90d", "ret_180d"]].set_index("cohort_month") * 100
            hm.columns = ["30d", "60d", "90d", "180d"]

            fig_hm = go.Figure(go.Heatmap(
                z=hm.values,
                x=hm.columns.tolist(),
                y=hm.index.tolist(),
                colorscale=[
                    [0.0, "#09090e"],
                    [0.3, "#2a1800"],
                    [0.6, "#7a5200"],
                    [1.0, "#f5c542"],
                ],
                zmin=0, zmax=8,
                text=hm.round(1).astype(str) + "%",
                texttemplate="%{text}",
                textfont=dict(size=9),
                hovertemplate="Cohort: %{y}<br>Period: %{x}<br>Retention: %{z:.1f}%<extra></extra>",
            ))
            for i, row in enumerate(cohorts_real.itertuples()):
                if row.is_outlier:
                    fig_hm.add_shape(type="rect",
                        x0=-0.5, x1=3.5, y0=i-0.5, y1=i+0.5,
                        line=dict(color="#ff5566", width=2))
                    fig_hm.add_annotation(x=3.6, y=i, text="⚠", showarrow=False,
                        font=dict(color="#ff5566", size=11), xanchor="left")

            fig_hm.update_layout(**plot_layout(
                title="Customers who bought again  ·  % who placed a 2nd order within X days",
                height=500,
                xaxis=dict(side="top"),
            ))
            st.plotly_chart(fig_hm, use_container_width=True)

        with col_c2:
            fig_ltv = go.Figure()
            for _, row in cohorts_real.iterrows():
                color   = "#ff5566" if row["is_outlier"] else COLORS["retention"]
                opacity = 1.0 if row["is_outlier"] else 0.25
                width   = 2.0 if row["is_outlier"] else 0.8
                fig_ltv.add_trace(go.Scatter(
                    x=[30, 60, 90, 180],
                    y=[row["ltv_30d"], row["ltv_60d"], row["ltv_90d"], row["ltv_180d"]],
                    mode="lines",
                    name=row["cohort_month"],
                    line=dict(color=color, width=width),
                    opacity=opacity,
                    showlegend=False,
                ))
            med = cohorts_real[["ltv_30d", "ltv_60d", "ltv_90d", "ltv_180d"]].median()
            fig_ltv.add_trace(go.Scatter(
                x=[30, 60, 90, 180],
                y=[med["ltv_30d"], med["ltv_60d"], med["ltv_90d"], med["ltv_180d"]],
                name="Median LTV",
                mode="lines+markers",
                line=dict(color=COLORS["retention"], width=2.5, dash="dash"),
                marker=dict(size=6),
            ))
            fig_ltv.update_layout(**plot_layout(
                title="LTV per Acquired Customer",
                height=280,
                xaxis=dict(title="Days since acquisition", tickvals=[30, 60, 90, 180]),
                yaxis=dict(title="LTV (BRL)"),
                legend=dict(orientation="h", y=1.15),
            ))
            st.plotly_chart(fig_ltv, use_container_width=True)


    # ── Section 2: Reviews ────────────────────────────────────────────────
    st.markdown('<div class="pillar-section"></div>', unsafe_allow_html=True)
    st.markdown("### Customer review quality")
    st.markdown(
        '<p class="kpi-label">Real Olist dataset · 104k reviews · Sep 2016 – Oct 2018</p>',
        unsafe_allow_html=True,
    )

    if rv_distribution is None:
        st.warning("Run `python scripts/build_olist_data.py` first.", icon="⚙️")
    else:
        total_reviews = int(rv_distribution["count"].sum())
        avg_score     = (rv_distribution["score"] * rv_distribution["count"]).sum() / total_reviews
        pct_5star     = rv_distribution.loc[rv_distribution["score"] == 5, "pct"].iloc[0]
        pct_1star     = rv_distribution.loc[rv_distribution["score"] == 1, "pct"].iloc[0]

        rk1, rk2, rk3, rk4 = st.columns(4)
        rk1.metric("Total Reviews", f"{total_reviews:,}")
        rk2.metric("Avg Score",     f"{avg_score:.2f} / 5")
        rk3.metric("5-Star Share",  f"{pct_5star:.1f}%")
        rk4.metric("1-Star Share",  f"{pct_1star:.1f}%", delta_color="inverse")

        col_rv1, col_rv2 = st.columns([2, 3])

        with col_rv1:
            SCORE_COLORS = ["#ff2244", "#ff6b6b", "#f5c542", "#3b9eff", "#22d3a0"]
            fig_dist = go.Figure(go.Bar(
                x=rv_distribution["score"].astype(str),
                y=rv_distribution["count"],
                marker_color=SCORE_COLORS,
                text=rv_distribution["pct"].map(lambda v: f"{v:.1f}%"),
                textposition="outside",
                hovertemplate="Score %{x}<br>%{y:,} reviews (%{text})<extra></extra>",
            ))
            fig_dist.update_layout(**plot_layout(
                title="Score Distribution",
                height=320,
                xaxis_title="Score",
                yaxis_title="Reviews",
            ))
            st.plotly_chart(fig_dist, use_container_width=True)

        with col_rv2:
            fig_rv_trend = go.Figure()
            fig_rv_trend.add_trace(go.Scatter(
                x=rv_monthly["review_creation_month"],
                y=rv_monthly["avg_score"],
                name="Avg score",
                mode="lines+markers",
                line=dict(color=COLORS["retention"], width=2),
                marker=dict(size=4),
            ))
            fig_rv_trend.add_trace(go.Bar(
                x=rv_monthly["review_creation_month"],
                y=rv_monthly["pct_1star"],
                name="1-star %",
                marker_color="rgba(255,34,68,0.30)",
                yaxis="y2",
            ))
            fig_rv_trend.update_layout(**plot_layout(
                title="Score Trend & 1-Star Share",
                height=320,
                xaxis=dict(tickangle=-45, nticks=10),
                yaxis=dict(title="Avg score", range=[3.0, 5.0]),
                yaxis2=dict(title="1-star %", overlaying="y", side="right", showgrid=False),
                legend=dict(orientation="h", y=1.18),
            ))
            st.plotly_chart(fig_rv_trend, use_container_width=True)

        if rv_by_category is not None:
            worst_cat_row = rv_by_category.loc[rv_by_category["avg_score"].idxmin()]
            best_cat_row  = rv_by_category.loc[rv_by_category["avg_score"].idxmax()]
            high_1star    = rv_by_category.loc[rv_by_category["pct_1star"].idxmax()]
            st.markdown(f"""
<div class="callout callout-red">
<strong>Lowest-rated category:</strong> {worst_cat_row['primary_category']}
— {worst_cat_row['avg_score']:.2f}★ avg, {worst_cat_row['pct_1star']:.1f}% one-star
across {int(worst_cat_row['orders']):,} orders.
Most dissatisfied: {high_1star['primary_category']} at {high_1star['pct_1star']:.1f}% one-star.
Best-rated: {best_cat_row['primary_category']} at {best_cat_row['avg_score']:.2f}★.
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# ORDER RISK
# ═══════════════════════════════════════════════════════════════════════════
if page == "💳 Payments":
    st.markdown("### Payment mix & cancellation risk")
    st.markdown(
        '<p class="kpi-label">Real Olist dataset · 99k orders · payment type, installments, cancellations</p>',
        unsafe_allow_html=True,
    )

    if pay_by_type is None:
        st.warning("Run `python scripts/build_olist_data.py` first.", icon="⚙️")
    else:
        cc_row    = pay_by_type[pay_by_type["payment_type"] == "credit_card"].iloc[0]
        bol_row   = pay_by_type[pay_by_type["payment_type"] == "boleto"].iloc[0]
        total_ord = pay_by_type["orders"].sum()
        total_can = pay_by_type["cancelled"].sum()
        high_inst = pay_installments.loc[pay_installments["cancellation_rate"].idxmax()]

        pk1, pk2, pk3, pk4 = st.columns(4)
        pk1.metric("Credit Card Share",   f"{cc_row['orders']/total_ord*100:.0f}%")
        pk2.metric("Boleto Share",        f"{bol_row['orders']/total_ord*100:.0f}%")
        pk3.metric("Overall Cancel Rate", f"{total_can/total_ord*100:.1f}%", delta_color="inverse")
        pk4.metric("Highest-Risk Bucket", high_inst["installment_bucket"],
                   f"{high_inst['cancellation_rate']*100:.1f}% cancel rate", delta_color="inverse")

        st.divider()
        col_pk1, col_pk2 = st.columns(2)

        with col_pk1:
            TYPE_LABELS = {
                "credit_card": "Credit Card",
                "boleto": "Boleto",
                "voucher": "Voucher",
                "debit_card": "Debit Card",
            }
            pbt = pay_by_type.copy()
            pbt["label"] = pbt["payment_type"].map(TYPE_LABELS).fillna(pbt["payment_type"])
            fig_paytype = go.Figure()
            fig_paytype.add_trace(go.Bar(
                name="Orders",
                x=pbt["label"], y=pbt["orders"],
                marker_color=COLORS["geo"],
                text=pbt["orders"].map(lambda v: f"{v:,}"),
                textposition="outside",
            ))
            fig_paytype.add_trace(go.Scatter(
                name="Cancel rate",
                x=pbt["label"], y=pbt["cancellation_rate"] * 100,
                mode="markers",
                marker=dict(color=COLORS["claimed"], size=14, symbol="diamond"),
                yaxis="y2",
            ))
            fig_paytype.update_layout(**plot_layout(
                title="Orders & Cancel Rate by Payment Type",
                height=360,
                yaxis=dict(title="Orders"),
                yaxis2=dict(title="Cancel %", overlaying="y", side="right", showgrid=False),
                legend=dict(orientation="h", y=1.15),
            ))
            st.plotly_chart(fig_paytype, use_container_width=True)

        with col_pk2:
            pi = pay_installments.copy()
            fig_inst = go.Figure()
            fig_inst.add_trace(go.Bar(
                name="Orders",
                x=pi["installment_bucket"], y=pi["orders"],
                marker_color="#9b72cf",
                text=pi["orders"].map(lambda v: f"{v:,}"),
                textposition="outside",
            ))
            fig_inst.add_trace(go.Scatter(
                name="Cancel rate",
                x=pi["installment_bucket"], y=pi["cancellation_rate"] * 100,
                mode="lines+markers",
                line=dict(color=COLORS["claimed"], width=2),
                marker=dict(size=8),
                yaxis="y2",
            ))
            fig_inst.update_layout(**plot_layout(
                title="Orders & Cancel Rate by Installment Count",
                height=360,
                yaxis=dict(title="Orders"),
                yaxis2=dict(title="Cancel %", overlaying="y", side="right", showgrid=False),
                legend=dict(orientation="h", y=1.15),
            ))
            st.plotly_chart(fig_inst, use_container_width=True)

        st.markdown("""
<div class="callout callout-red">
<strong>Risk signal:</strong> Orders split across 13–24 installments have the highest cancellation rate
in the dataset. High-installment boleto orders carry dual risk: payment may not settle, and the
customer is committed to a long repayment window. These orders warrant additional fulfilment
verification before shipping.
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# SELLERS
# ═══════════════════════════════════════════════════════════════════════════
if page == "🏪 Sellers":
    st.markdown("### Seller performance & revenue concentration")
    st.markdown(
        '<p class="kpi-label">Real Olist dataset · 1,238 qualifying sellers · 10+ orders each</p>',
        unsafe_allow_html=True,
    )

    if seller_perf is None:
        st.warning("Run `python scripts/build_olist_data.py` first.", icon="⚙️")
    else:
        total_rev_s = seller_perf["revenue"].sum()
        top10_share = seller_perf.head(10)["revenue"].sum() / total_rev_s * 100
        avg_score_s = np.average(seller_perf["avg_review_score"], weights=seller_perf["orders"])
        sp_share    = (seller_perf[seller_perf["seller_state"] == "SP"]["orders"].sum()
                       / seller_perf["orders"].sum() * 100)

        sk1, sk2, sk3, sk4 = st.columns(4)
        sk1.metric("Qualifying Sellers",   f"{len(seller_perf):,}")
        sk2.metric("Top 10 Revenue Share", f"{top10_share:.1f}%")
        sk3.metric("Avg Review Score",     f"{avg_score_s:.2f}★")
        sk4.metric("SP Seller Share",      f"{sp_share:.0f}% of orders")

        st.divider()
        col_s1, col_s2 = st.columns([3, 2])

        with col_s1:
            fig_scatter_s = px.scatter(
                seller_perf.head(200),
                x="revenue", y="avg_review_score",
                size="orders", color="on_time_rate",
                color_continuous_scale="RdYlGn",
                hover_name="seller_id",
                hover_data={
                    "seller_state": True,
                    "top_category": True,
                    "orders": ":,",
                    "revenue": ":,.0f",
                    "on_time_rate": ":.1%",
                    "avg_review_score": ":.2f",
                },
                labels={
                    "revenue": "Revenue (BRL)",
                    "avg_review_score": "Avg review score",
                    "on_time_rate": "On-time",
                },
                size_max=30,
            )
            fig_scatter_s.update_layout(**plot_layout(
                title="Revenue vs Review Score  (top 200 sellers · colour = on-time rate)",
                height=420,
                coloraxis_colorbar=dict(title="On-time", tickformat=".0%", thickness=10),
            ))
            st.plotly_chart(fig_scatter_s, use_container_width=True)

        with col_s2:
            fig_pareto = go.Figure(go.Scatter(
                x=list(range(1, len(seller_conc) + 1)),
                y=seller_conc["cumulative_revenue_pct"],
                mode="lines",
                fill="tozeroy",
                fillcolor="rgba(124,107,255,0.15)",
                line=dict(color=COLORS["attribution"], width=2),
                hovertemplate="Top %{x} sellers<br>%{y:.1f}% of revenue<extra></extra>",
            ))
            fig_pareto.add_hline(y=80, line_dash="dot",
                line_color="#f5c542", annotation_text="80%",
                annotation_position="right")
            fig_pareto.update_layout(**plot_layout(
                title="How many sellers drive 80% of revenue",
                height=420,
                xaxis=dict(title="Seller rank"),
                yaxis=dict(title="Cumulative revenue %", range=[0, 101]),
            ))
            st.plotly_chart(fig_pareto, use_container_width=True)

        with st.expander("Worst-rated sellers (min 50 orders)"):
            worst_sellers = (
                seller_perf[seller_perf["orders"] >= 50]
                .nsmallest(12, "avg_review_score")
                [["seller_id", "seller_state", "top_category", "orders",
                  "revenue", "on_time_rate", "avg_review_score"]]
                .copy()
            )
            worst_sellers["revenue"]          = worst_sellers["revenue"].map(lambda v: f"R${v:,.0f}")
            worst_sellers["on_time_rate"]     = worst_sellers["on_time_rate"].map(lambda v: f"{v*100:.1f}%")
            worst_sellers["avg_review_score"] = worst_sellers["avg_review_score"].map(lambda v: f"{v:.2f}★")
            worst_sellers["seller_id"]        = worst_sellers["seller_id"].str[:12] + "…"
            st.dataframe(worst_sellers, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════
# CHARGEBACK RISK
# ═══════════════════════════════════════════════════════════════════════════
if page == "🚨 Risk":
    st.markdown("### Dispute & chargeback risk — order-level flagging")
    st.markdown(
        '<p class="kpi-label">Real Olist dataset · delivered orders only · 3-signal evidence model</p>',
        unsafe_allow_html=True,
    )

    st.markdown("""
<div class="callout callout-red">
<strong>How orders are flagged:</strong> An order scores one point for each of three independent
dispute signals — <strong>1-star review</strong>, <strong>delivered 7+ days late</strong>,
<strong>7+ installment payment</strong>. Orders with 2 or 3 signals are flagged as high-confidence
chargeback proxies. Merchants lose ~80% of disputes; the average loss is R$800/month.
</div>
""", unsafe_allow_html=True)

    if cb_monthly_df is None:
        st.warning("Run `python scripts/build_olist_data.py` first.", icon="⚙️")
    else:
        total_flagged   = int(cb_monthly_df["flagged_orders"].sum())
        total_at_risk   = cb_monthly_df["flagged_revenue"].sum()
        avg_flag_rate   = (cb_monthly_df["flagged_orders"].sum() /
                           cb_monthly_df["total_orders"].sum() * 100)
        avg_flagged_rev = total_at_risk / total_flagged if total_flagged else 0
        worst_cat       = cb_category_df.iloc[0]["primary_category"] if cb_category_df is not None else "—"

        ck1, ck2, ck3, ck4 = st.columns(4)
        ck1.metric("Flagged Orders",       f"{total_flagged:,}",
                   "2+ risk signals each", delta_color="inverse")
        ck2.metric("Revenue at Risk",      f"R${total_at_risk:,.0f}",
                   "across all flagged orders", delta_color="inverse")
        ck3.metric("Flag Rate",            f"{avg_flag_rate:.1f}%",
                   "of delivered orders", delta_color="inverse")
        ck4.metric("Highest-Risk Category", worst_cat)

        st.divider()
        col_cb1, col_cb2 = st.columns([3, 2])

        with col_cb1:
            fig_cb_monthly = go.Figure()
            fig_cb_monthly.add_trace(go.Bar(
                x=cb_monthly_df["purchase_month"],
                y=cb_monthly_df["flagged_orders"],
                name="Flagged orders",
                marker_color="rgba(255,85,102,0.7)",
                hovertemplate="%{x}<br>%{y} flagged orders<extra></extra>",
            ))
            fig_cb_monthly.add_trace(go.Scatter(
                x=cb_monthly_df["purchase_month"],
                y=cb_monthly_df["flagged_revenue"],
                name="Revenue at risk (BRL)",
                mode="lines+markers",
                line=dict(color="#f5c542", width=2),
                marker=dict(size=5),
                yaxis="y2",
            ))
            fig_cb_monthly.update_layout(**plot_layout(
                title="Monthly flagged orders and revenue at risk",
                height=340,
                yaxis=dict(title="Flagged orders"),
                yaxis2=dict(title="Revenue at risk (BRL)", overlaying="y",
                            side="right", showgrid=False),
                legend=dict(orientation="h", y=1.15),
            ))
            st.plotly_chart(fig_cb_monthly, use_container_width=True)

        with col_cb2:
            if cb_evidence_df is not None:
                score_labels = {0: "No signals", 1: "1 signal", 2: "2 signals ⚠", 3: "All 3 signals 🚨"}
                ev = cb_evidence_df.copy()
                ev["label"]   = ev["risk_score"].map(score_labels)
                ev["revenue_m"] = ev["revenue"] / 1e6

                bar_colors = ["#2a2a40", "#444466", "#ff8a4c", "#ff5566"]
                fig_ev = go.Figure(go.Bar(
                    x=ev["label"],
                    y=ev["orders"],
                    marker_color=bar_colors[:len(ev)],
                    text=ev["orders"].map(lambda v: f"{v:,}"),
                    textposition="outside",
                    customdata=ev["revenue_m"],
                    hovertemplate="%{x}<br>%{y:,} orders<br>R$%{customdata:.1f}M revenue<extra></extra>",
                ))
                fig_ev.update_layout(**plot_layout(
                    title="Orders by number of risk signals",
                    height=340,
                    xaxis_title="Evidence level",
                    yaxis_title="Orders",
                ))
                st.plotly_chart(fig_ev, use_container_width=True)

        # ── Category risk ─────────────────────────────────────────────────
        if cb_category_df is not None:
            st.markdown("#### Categories with the highest dispute risk")
            col_cb3, col_cb4 = st.columns([3, 2])

            with col_cb3:
                top_cats = cb_category_df.head(15).copy()
                top_cats["label"] = top_cats["primary_category"].str.replace("_", " ").str.title()

                fig_cat_risk = go.Figure(go.Bar(
                    x=top_cats["flag_rate"] * 100,
                    y=top_cats["label"],
                    orientation="h",
                    marker_color=top_cats["flag_rate"].apply(
                        lambda v: "#ff5566" if v > 0.05 else ("#ff8a4c" if v > 0.03 else "#f5c542")
                    ),
                    text=top_cats["flag_rate"].map(lambda v: f"{v*100:.1f}%"),
                    textposition="auto",
                    customdata=top_cats["flagged_revenue"],
                    hovertemplate="%{y}<br>Flag rate: %{x:.1f}%<br>Revenue at risk: R$%{customdata:,.0f}<extra></extra>",
                ))
                fig_cat_risk.update_layout(**plot_layout(
                    title="Flag rate by category  (red > 5%, amber > 3%)",
                    height=420,
                    xaxis=dict(title="% of orders flagged"),
                    yaxis=dict(title=""),
                ))
                st.plotly_chart(fig_cat_risk, use_container_width=True)

            with col_cb4:
                top5_rev = (cb_category_df
                            .nlargest(8, "flagged_revenue")
                            [["primary_category", "flagged_revenue", "flagged_orders", "flag_rate"]]
                            .copy())
                top5_rev["flagged_revenue"] = top5_rev["flagged_revenue"].map(lambda v: f"R${v:,.0f}")
                top5_rev["flag_rate"]       = top5_rev["flag_rate"].map(lambda v: f"{v*100:.1f}%")
                top5_rev["primary_category"] = top5_rev["primary_category"].str.replace("_", " ").str.title()
                top5_rev.columns = ["Category", "Revenue at Risk", "Flagged Orders", "Flag Rate"]
                st.markdown("**Highest revenue at risk by category**")
                st.dataframe(top5_rev, use_container_width=True, hide_index=True)

                st.markdown("""
<div class="callout callout-red" style="margin-top:16px">
<strong>Action:</strong> Categories with both high flag rate and high revenue at risk
are the priority intervention. A pre-shipment review policy on flagged orders
in these categories is the highest-ROI first step.
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# AI BRIEF
# ═══════════════════════════════════════════════════════════════════════════
if page == "🤖 Executive Brief":
    st.markdown("### Weekly Commerce Brief — AI-Generated")
    st.markdown("""
<div class="callout">
This is the packaged AI layer for Commerce Leak Studio. It turns the queue and
dashboard metrics into a client-ready weekly brief. Demo mode stays available
when live API quota is unavailable.
</div>
""", unsafe_allow_html=True)

    col_b1, col_b2, col_b3, col_b4 = st.columns(4)
    col_b1.metric("MER this week",   f"{last_week['mer']:.2f}x",
                  delta=f"{(last_week['mer']-prev_week['mer']):.2f} vs prev")
    col_b2.metric("Shopify revenue", f"R${last_week['shopify_revenue']:,.0f}",
                  delta=f"{(last_week['shopify_revenue']/prev_week['shopify_revenue']-1)*100:+.1f}%")
    col_b3.metric("Total spend",     f"R${last_week['total_spend']:,.0f}",
                  delta=f"{(last_week['total_spend']/prev_week['total_spend']-1)*100:+.1f}%")
    col_b4.metric("Overclaim",       f"+{last_week['overclaim_pct']:.0f}%",
                  delta="platforms vs Shopify", delta_color="inverse")

    st.divider()

    col_gen1, col_gen2 = st.columns([1, 3])
    with col_gen1:
        generate_btn = st.button("Generate Live Brief", type="primary", use_container_width=True, key="tab_ai_generate")

    brief_placeholder = st.empty()

    if generate_btn:
        generate_openai_brief(api_key, prompt_context, brief_placeholder)
    else:
        brief_placeholder.markdown(
            render_brief_box(DEMO_BRIEF, 0.68, "Demo output shown while live AI is unavailable or quota-limited:"),
            unsafe_allow_html=True,
        )

    st.divider()
    st.markdown("#### What the prompt sends to the model")
    with st.expander("View prompt context"):
        st.code(prompt_context, language="text")
