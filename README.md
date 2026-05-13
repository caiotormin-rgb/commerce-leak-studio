# Commerce Leak Studio

A working ecommerce attribution analytics demo modeled on the real
[Olist Brazilian ecommerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).

Packaged as a Torm Data Co. product for a mock retailer, **Luma & Co.**,
a Brazilian home, gifts, and lifestyle marketplace.

Promise: find the profit leaks hiding between marketing, fulfillment, and retention.

## What it shows

**Tab 1 — Sales Performance**
General sales overview: revenue, orders, AOV, weekly trend, monthly seasonality,
and category mix.

**Tab 2 — The Attribution Lie**
Platform-reported revenue vs Shopify ground truth. Meta + Google + Email collectively
claim ~140% of actual revenue. The demo makes this visceral with charts and math.

**Tab 3 — MER Reality**
Media Efficiency Ratio (Total Revenue ÷ Total Spend) as the north star metric that
sidesteps platform self-reporting entirely. Includes anomaly detection and
spend-mix correlation analysis.

**Tab 4 — Reviews**
Review score trends, low-star review share, response time patterns, and category
quality weak spots.

**Tab 5 — Geo Patterns**
State and region demand patterns with delivery friction, late-delivery rate,
review score, and return-rate overlays.

**Tab 6 — Returns**
Return rate, refund value, return reasons, and category-level return risk.

**Tab 7 — Cohort Intelligence**
Monthly cohort retention heatmap + LTV curves. A March 2017 anomaly is baked in:
a Meta broad-targeting spike brought high-volume, low-quality customers — visible
as 3× lower 90d retention vs every other cohort.

**Tab 8 — Fulfillment Intelligence** *(real Olist data)*
Delivery SLA performance from the actual Olist dataset. Core insight: on-time
orders average 4.3★, orders 8–14 days late drop to 1.7★. Includes review score
× lateness correlation, monthly trend, and category-level on-time scatter.

**Tab 9 — Geo Intelligence** *(real Olist data)*
Geographic demand and delivery patterns by Brazilian state. Revenue concentration,
delivery speed by state, late delivery rates, and buyer/seller coverage gaps
(PA has 922 buyers per 1 seller — most underserved market in the dataset).

**Top-level — This Week's Leaks**
Owner-ready action queue ranking attribution, fulfillment, retention, payment,
chargeback, and seller-quality leaks by estimated impact.

**Top-level — AI Brief Studio**
Prominent AI panel that turns the action queue into an executive commerce brief.
Enter an OpenAI API key in the sidebar to generate live. If quota is unavailable,
the app falls back to a polished demo brief instead of blocking the experience.

**Tab 10 — AI Brief**
Expanded prompt view and live/demo weekly commerce brief using metrics and the
action queue from the dashboard.

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

The top-level "This Week's Leaks" queue and AI Brief Studio turn dashboard signals
into owner-ready actions across growth, fulfillment, retention, payment risk,
chargeback risk, and seller quality.

No real customer data. Safe to share publicly.

## Stack

| Layer | Tool |
|---|---|
| Data generation | numpy / pandas |
| In-process SQL | DuckDB |
| UI | Streamlit |
| Charts | Plotly |
| AI brief | OpenAI Responses API |
| Hosting | Streamlit Community Cloud |
