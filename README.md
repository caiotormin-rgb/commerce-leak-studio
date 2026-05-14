# Margin Intelligence Report

A working ecommerce operating analytics demo modeled on the real
[Olist Brazilian ecommerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).

Packaged as a Torm Data Co. product for a mock retailer, **Casa Viva**,
a Brazilian home, gifts, and lifestyle marketplace.

**Core thesis:** find the profit leaks hiding between marketing, fulfillment, and retention — then name a specific owner and action for each one.

---

## Sections

Navigation lives in the sidebar. Each section is a focused view into one part of the operating story.

**Executive Brief**
The full operating story in one screen: spend → delivery → repeat purchase, with a prioritised Opportunities queue ranking each leak by estimated revenue impact, owner, and confidence. AI Brief Studio (sidebar) turns the live queue into a client-ready 600-word weekly brief via OpenAI.

**Revenue**
Baseline revenue context: Shopify revenue, orders, AOV, weekly trend, and category mix.

**Categories**
Product category deep-dive: revenue mix over time, growth by category (last 4 weeks vs prior 4), return rates and refund value, return reasons by category, and a composite health scorecard combining review quality (40%), on-time delivery (30%), and chargeback flag rate (30%).

**Demand**
Monthly demand cycles, seasonal index, year-over-year order trends, and category demand mix.

**Attribution**
Platform-reported revenue vs Shopify ground truth, MER anomaly detection, spend mix by channel, and GA4 tracking gap analysis.

**Retention**
Cohort repeat rates and LTV curves, review score distribution and trend, and category-level review quality.

**Fulfillment**
Delivery lateness impact on reviews, monthly delivery trend, on-time rate by category, and geographic seller/order coverage.

**Payments**
Payment type mix, installment bracket cancellation risk, and payment patterns by category and state.

**Sellers**
Seller quality distribution, revenue concentration (top-N sellers), and worst-rated seller table with revenue at risk.

**Risk**
Three-signal chargeback proxy model (1-star review + 7+ days late + 7+ installments), monthly flagged orders and revenue at risk, and category flag rates.

**Agent Prototypes**
Seven agentic automations derived directly from the leaks in this dashboard. Each one runs on a schedule, detects a specific problem, and takes a concrete action — internal ticket, department email, automatic email, or gift card issuance. Total opportunity modeled: R$1.1M+.

| Agent | Problem it solves | Actions |
| --- | --- | --- |
| Chargeback Triage | Rising flag rates ship before anyone notices | Internal ticket, email to dept |
| Repeat Customer Detector | Cohort drop goes unexplained for months | Issue gift card, email to dept |
| Budget Reallocation Advisor | Quarterly budget guess ignores fraud and LTV | Internal ticket, email to dept |
| Seller Health Monitor | SLA breaches accumulate before ops is alerted | Send auto email, internal ticket |
| Review Crisis Responder | 1-star spike misread as delivery, not product | Auto email, gift card, email to dept |
| Geo Expansion Scout | High-demand states have too few local sellers | Internal ticket, email to dept |
| Manufacturer Escalation | Product defects misattributed to fulfillment | Auto email to manufacturer, internal ticket |

---

## Run locally

```bash
pip install -r requirements.txt

# Build real Olist data files — run once, takes ~15s
python scripts/build_olist_data.py

streamlit run app.py
```

Without the build step the app runs on synthetic data only (attribution and categories sections). The fulfillment, reviews, cohorts, payments, sellers, and risk sections unlock after the build.

## Deploy to Streamlit Cloud

1. Push repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app → connect repo
3. Set main file: `app.py`
4. Deploy — public URL in ~2 minutes

To enable live AI brief generation, add `OPENAI_API_KEY` as a secret in the Streamlit Cloud dashboard (Settings → Secrets). Without it, the demo brief still works.

---

## Data notes

| Signal | Source | Notes |
| --- | --- | --- |
| Attribution (spend, MER, overclaim) | Synthetic | Modeled on Olist revenue scale; platforms overclaim by design |
| Fulfillment, geography | Real Olist | ~100k orders, 2016–2018 |
| Reviews, cohorts | Real Olist | ~100k reviews linked to orders |
| Payments, sellers | Real Olist | Full payment and seller tables |
| Categories (revenue mix) | Synthetic | Same seed as attribution; consistent week-over-week |
| Returns | Synthetic | Modeled on Olist return patterns by category and reason |

Synthetic attribution assumptions:

- Meta overclaims ~45% (view-through attribution window abuse)
- Google overclaims ~25% (PMax cross-channel double-counting)
- GA4 missing ~22% of orders (client-side tracking gaps, iOS ITP, ad blockers)
- March 2017 cohort: deliberately low retention from broad targeting

No real customer data. Safe to share publicly.

---

## Code structure

```text
app.py          — routing, data loading, sidebar, action queue computation
shared.py       — constants, helpers (brl, plot_layout, render_brief_box, etc.)
views/
  executive_brief.py   — operating story, opportunities queue, AI brief
  revenue.py    → sales.py
  categories.py        — category health, returns, revenue mix
  demand.py            — seasonality
  spend.py             — attribution / MER
  customers.py         — retention / cohorts
  delivery.py          — fulfillment
  payments.py
  sellers.py
  risk.py              — chargeback model
  agents.py            — agent prototypes carousel
data_gen.py     — synthetic data generation (weekly, categories, returns)
scripts/
  build_olist_data.py  — real Olist CSV → parquet pipeline
```

Each view module exports a single `render(**kwargs)` function. `app.py` handles all data loading, filtering, and routing; views receive only what they display.

---

## Stack

| Layer | Tool |
|---|---|
| Data generation | numpy / pandas |
| In-process SQL | DuckDB |
| UI | Streamlit ≥ 1.35 |
| Charts | Plotly |
| AI brief | OpenAI `gpt-4o-mini` (streaming) |
| Hosting | Streamlit Community Cloud |
