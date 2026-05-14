# Retail Pulse

A working ecommerce attribution analytics demo modeled on the real
[Olist Brazilian ecommerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).

Packaged as a Torm Data Co. product for a mock retailer, **Luma & Co.**,
a Brazilian home, gifts, and lifestyle marketplace.

Promise: find the profit leaks hiding between marketing, fulfillment, and retention.

## What it shows

**Tab 1 — Client Brief**
Live/demo weekly commerce brief using the current metrics and action queue.

**Tab 2 — Evidence: Sales**
Baseline revenue context: revenue, orders, AOV, weekly trend, and category mix.

**Tab 3 — Evidence: Demand**
Monthly demand cycles, seasonal index, year-over-year orders, and category demand mix.

**Tab 4 — Evidence: Spend**
Platform-reported revenue vs Shopify ground truth, MER anomaly detection, spend mix,
and GA4 tracking gap.

**Tab 5 — Evidence: Customers**
Cohort retention, LTV curves, review distribution, score trends, and category quality.

**Tab 6 — Evidence: Delivery**
Delivery lateness impact on reviews, monthly delivery trend, and geographic coverage.

**Tab 7 — Evidence: Payments**
Payment type and installment cancellation risk.

**Tab 8 — Evidence: Sellers**
Seller quality, revenue concentration, and worst-rated seller table.

**Tab 9 — Evidence: Risk**
Three-signal chargeback proxy model, monthly risk trend, and category revenue at risk.

**Top-level — Home story**
An editorial story spine shows the operating flow from spend to delivery to
repeat purchase, then names the single highest-priority next move. Supporting
actions and source coverage sit behind an expander.

**Top-level — AI Brief Studio**
Primary AI button that turns the current story and action queue into an executive
commerce brief.
Enter an OpenAI API key in the sidebar to generate live with `gpt-oss-20b`.
If quota is unavailable, the app falls back to a polished demo brief instead of
blocking the experience.

## Run locally

```bash
pip install -r requirements.txt
# Build the real data files (run once, ~15s)
python scripts/build_olist_data.py
streamlit run app.py
```

The app defaults to a fast synthetic dataset calibrated to Olist so Streamlit
Cloud cold starts do not parse the full CSV bundle. To explore the raw CSV path
locally, run with `USE_REAL_OLIST=1`.

## Deploy to Streamlit Cloud (free)

1. Push to GitHub
2. Go to share.streamlit.io → New app → connect repo
3. Set main file: `app.py`
4. Deploy — public URL in ~2 min

## Data notes

Data is sourced from the real Olist Brazilian ecommerce dataset. Attribution metrics
are synthetic to demonstrate common platform overclaiming issues:

- Meta overclaims ~45% (view-through attribution window abuse)
- Google overclaims ~25% (PMax cross-channel double-counting)  
- GA4 missing ~22% of orders (client-side tracking gaps, iOS ITP, ad blockers)
- March 2017 cohort: low retention from broad Meta targeting

The top-level story and AI Brief Studio turn dashboard signals into owner-ready
actions across growth, fulfillment, retention, payment risk, chargeback risk,
and seller quality.

No real customer data. Safe to share publicly.

## Stack

| Layer | Tool |
|---|---|
| Data generation | numpy / pandas |
| In-process SQL | DuckDB |
| UI | Streamlit |
| Charts | Plotly |
| AI brief | OpenAI Responses API with `gpt-oss-20b` |
| Hosting | Streamlit Community Cloud |
