# Demo Build Process

How we went from a market research report to working dashboard tabs.

---

## 1. Research Input

Source: a synthesised Reddit market research report covering 18 communities
(r/shopify, r/SaaS, r/ecommerce, r/AmazonSeller, etc., ~15M combined members).

The report scored 47 pain points and ranked 10 product opportunities. The three
structural findings that shaped what we built:

| Finding | Signal |
|---|---|
| CAC crisis | Universal across all communities — paid acquisition up 40–60% since 2023 |
| Attribution broken | Meta + GA4 data diverge 30–50%; last-click misses community/dark social |
| Platform risk anxiety | Shopify holds, Amazon suspensions, fee hikes — merchants feel exposed |

Top-ranked opportunity: **automated chargeback defence for Shopify** (merchants lose
~80% of disputes, $800/month average loss, no automated tool exists).

---

## 2. Use Case Selection

From the report, six use cases were identified as demo-viable (meaning: could be
shown as a plug-and-play dashboard, not a consulting engagement):

| Use case | Report rank | Demo viability |
|---|---|---|
| Attribution dashboard | #2 (post-iOS14) | High — directly maps to ad spend data |
| Chargeback / dispute defence | #1 | Medium — needs real dispute data |
| Customer retention & LTV | Cross-cutting | High — standard cohort analysis |
| App stack auditor | #5 | Low for dashboard (output is a list, not a chart) |
| Cart abandonment intelligence | Cross-cutting | Medium — needs session-level data |
| Fulfillment & delivery intelligence | Cross-cutting | High — timestamp data is widely available |

The three chosen for this build:

> **Attribution → Fulfillment → Retention** as a connected narrative:
> you acquired customers (attribution), delivered to them (fulfillment),
> and almost none came back (retention). Three panels, one story.

Geographic analysis was added as a fourth because the dataset had strong
state-level data and the coverage-gap story (buyers per seller by state) is
a concrete operational finding, not just a vanity metric.

---

## 3. Dataset Analysis

Dataset: **Olist Brazilian E-commerce** (public, Kaggle). 9 CSV files.

```
olist_orders_dataset.csv          99,441 orders  — status, 4 timestamps
olist_order_items_dataset.csv    112,650 items   — price, freight, product_id
olist_order_payments_dataset.csv 103,886 rows    — payment type, installments
olist_customers_dataset.csv       99,441 rows    — city, state
olist_order_reviews_dataset.csv  104,719 rows    — score 1–5, optional text
olist_products_dataset.csv        32,951 rows    — category (Portuguese)
olist_sellers_dataset.csv          3,095 rows    — seller state
olist_geolocation_dataset.csv  1,000,163 rows   — zip → lat/lng
product_category_name_translation.csv  70 rows  — PT → EN category names
```

Key facts discovered in exploration:

| Fact | Value |
|---|---|
| Date range | Sep 2016 – Oct 2018 |
| Order statuses | 97% delivered, 0.6% cancelled, 0.3% unavailable |
| On-time delivery rate | 91.9% |
| Repeat customer rate | 3.1% (low — this is the retention story) |
| Review distribution | 55% give 5★, 11% give 1★ |
| Top payment type | Credit card 74%, boleto 19% |
| Top state by orders | SP 38%, RJ 12%, MG 11% |

**What the data can do natively:**
- Delivery SLA analysis (all 4 timestamps present)
- Review score correlation with delivery lateness
- Geographic breakdown by state (customer + seller + geo coordinates)
- Category performance (revenue, freight ratio, review scores)
- Cohort retention (customer_unique_id allows repeat-purchase tracking)

**What needs simulation:**
- Marketing channel attribution (no UTM/source data in Olist)
- Chargeback disputes (no dispute records; can use 1-star + cancellation as proxy)
- Cart sessions (no session data; only completed + cancelled orders)

The existing app (`data_gen.py`) already handles attribution with a realistic
synthetic model (Meta overclaims 45%, Google 25%, GA4 missing 22%). That model
is better than assigning random channels to the real orders, so attribution tabs
were left as synthetic. New tabs use real data.

---

## 4. Data Pipeline

**[scripts/build_olist_data.py](scripts/build_olist_data.py)** — run once before starting the app.

```bash
python scripts/build_olist_data.py
```

What it does:

1. Loads all 9 CSVs
2. Joins: orders + items (revenue) + products (English category) + customers (state) + reviews (score)
3. Computes delivery metrics: `delivered_on_time`, `delivery_days`, `days_late`
4. Aggregates into 4 output files:

| Output file | Contents | Rows |
|---|---|---|
| `data/fulfillment_review_lateness.csv` | Avg review score per lateness bucket | 5 |
| `data/fulfillment_by_category.csv` | On-time rate, delivery days, review score, revenue per category | 43 |
| `data/fulfillment_monthly.csv` | Monthly trend: on-time rate, avg days, avg review | 22 |
| `data/geo_state_real.csv` | Revenue, orders, customers, sellers, delivery stats per state | 27 |

Runtime: ~10–15 seconds on the full 1.5M-row dataset.

The app loads these files with `@st.cache_data` — no reprocessing on page reload.
If the files are missing, tabs show a build instruction instead of crashing.

---

## 5. Dashboard Design

### Product package

The demo is packaged as **Margin Intelligence Report** by **Torm Data Co.** for a mock
retailer, **Casa Viva** The identity is intentionally code-native: a simple `L`
mark, a restrained dark operating-console palette, and product copy focused on
finding profit leaks across marketing, fulfillment, retention, and risk.

The AI layer is presented as **AI Brief Studio**. It can generate live briefs with
an OpenAI key, but it also includes a quota-safe demo mode so prospects can still
see the product narrative when API quota or billing is unavailable.

### Tab: Fulfillment Intelligence

**Core insight:** delivery lateness is the primary driver of bad reviews.

| Lateness bucket | Avg review score | Orders |
|---|---|---|
| On time | 4.29 ★ | 89,451 |
| 1–3 days late | 3.29 ★ | 1,852 |
| 4–7 days late | 2.11 ★ | 1,748 |
| 8–14 days late | 1.67 ★ | 1,446 |
| 14+ days late | 1.73 ★ | 1,335 |

Every late delivery is a review bomb. Review score drives repeat purchase.
This makes fulfillment SLA a direct LTV lever, not just an ops metric.

Charts:
- Bar chart: review score × lateness bucket (the key insight, front and centre)
- Dual-axis line: on-time rate + avg delivery days monthly trend
- Scatter: on-time rate × review score by category (size = volume, colour = speed)
- Ranked bar: worst on-time rate categories

### Tab: Geo Intelligence

**Core insight:** Northern/Northeastern states have the longest delivery times,
lowest review scores, and the fewest sellers relative to buyer demand.

Key finding: PA (Pará) has 922 buyers per seller — the most underserved market
in the dataset. AL (Alagoas) has the highest late delivery rate.

Charts:
- Bubble map of Brazil: size = revenue, colour = late delivery % by state
- Ranked horizontal bar: avg delivery days by state (red/yellow/green)
- Buyers-per-seller gap by state (coverage opportunity)
- Lowest review score by state

---

## 6. Architecture

The app has two data layers:

```
Synthetic (data_gen.py)              Real (scripts/build_olist_data.py)
────────────────────────             ──────────────────────────────────
Sales Performance                    Fulfillment Intelligence
The Attribution Lie                  Geo Intelligence
MER Reality
Reviews
Geo Patterns (synthetic)
Returns
Cohort Intelligence
AI Brief
```

Synthetic is used for attribution tabs because:
- Olist has no channel/UTM data
- The synthetic model has deliberate attribution problems baked in
  (Meta overclaims, GA4 gap, anomaly cohort) that make the demo narrative work
- A synthetic attribution story is more compelling than randomly assigned channels

Real data is used for fulfillment and geo because:
- The timestamps, categories, and geography are genuinely rich
- The review-lateness correlation is real and striking
- The geographic coverage gaps are real operational findings

---

## 7. Files Changed

| File | Change |
|---|---|
| `scripts/build_olist_data.py` | New — aggregation pipeline for real Olist data |
| `data/*.csv` | Generated — 4 pre-aggregated files (gitignored or reproducible) |
| `app.py` | Added `load_fulfillment_data()`, `load_geo_real()`, two new tabs |
| `README.md` | Updated tab list to include new tabs |

---

## 8. Next Steps

Immediate:

- [ ] Chargeback risk tab: flag orders with 1★ review + late delivery + high-installment payment as dispute proxies. Show projected monthly loss, categories at highest risk, evidence strength score per order.
- [ ] Cart abandonment proxy: use `order_status = cancelled/unavailable` + payment type as a lightweight abandonment signal until session data is available.

Medium term:

- [ ] HTML/JS version of the three strongest tabs (Attribution Lie, Fulfillment, Geo) for external sharing without requiring a Python runtime.
- [ ] Real channel data: connect a live Shopify + Meta export to replace the synthetic attribution layer with actual UTM/source data.
- [ ] Seller performance tab: on-time rate, review score, and revenue per seller — shows which sellers are dragging down the marketplace average.
