# Commerce Leak Studio Spec
**File:** `app.py` · **Build:** `python scripts/build_olist_data.py` · **Run:** `streamlit run app.py`

---

## Product identity

| Element | Detail |
|---|---|
| Consultancy | `Torm Data Co.` |
| Product | `Commerce Leak Studio` |
| Mock retailer | `Luma & Co.` |
| Retailer category | Brazilian home, gifts, and lifestyle marketplace |
| Promise | "Find the profit leaks hiding between marketing, fulfillment, and retention." |
| Logo system | Code-native `L` mark in emerald / amber / indigo, paired with Luma & Co. wordmark |

## Global — always visible

### Sidebar
| Element | Detail |
|---|---|
| Brand card | Luma & Co. mock retailer identity + product byline |
| Period slider | Filters synthetic weekly data only. Real Olist tabs ignore it. |
| AI Brief Studio | OpenAI key field + quota-safe demo-mode note. Used by top AI panel and AI Brief tab. Live model: `gpt-oss-20b`. |

### Home story — narrative spine
Replaces the prior KPI strip and boxed flow. Renders as one editorial story block above the tabs.

| Beat | Accent | Primary metric | Supporting line |
|---|---|---|---|
| Spend | `#7c6bff` | `MER {x:.2f}x` | media spend, revenue, platform overclaim |
| Delivery | `#22d3a0` | `{on_time:.1f}% on time` | order volume and average delivery days |
| Repeat | `#f5c542` | `{repeat:.1f}% repeat` | customer count and 180d LTV |
| Next move | neutral | top action queue leak | owner, impact, recommended action |

### Supporting action queue
Hidden inside "Supporting action queue and source coverage". It converts dashboard signals into an owner-ready operating queue.

| Column | Detail |
|---|---|
| Priority | `P1` or `P2` |
| Leak | Business issue detected |
| Impact | BRL estimate or proxy from the available aggregate data |
| Owner | Growth, Ops, Retention, Finance, Marketplace Ops |
| Recommended action | One concrete next step with a number where possible |
| Confidence | High / Medium |
| Source | Synthetic attribution, fulfillment, cohorts, payments, seller performance, or risk signals |

Current queue inputs:
- Platform overclaim: `sum(total_claimed) - sum(shopify_revenue)`
- Late delivery review damage: late-order count × average real Olist order value
- One-time buyer churn: upside from moving 180d repeat rate toward 5.0%
- Chargeback exposure: `sum(flagged_revenue)`
- Payment cancellation risk: highest installment cancellation bucket × average value
- Seller quality drag: highest-revenue seller with ≥50 orders and low review score

### Data trust
Shown inside the same supporting expander as the action queue.

### AI Brief Studio — primary CTA
Renders as a single primary button under the home story and above the tab bar.

| Element | Detail |
|---|---|
| Status | `Live key provided` if sidebar key exists, else `Demo mode` |
| Button | `Generate client brief` primary button |
| Live behavior | Calls OpenAI Responses API with the same prompt used in Tab 9 and `model="gpt-oss-20b"` |
| Quota behavior | If OpenAI returns quota / rate-limit / billing errors, render quota-safe demo brief instead of stopping at the error |
| Default behavior | Keeps homepage quiet; full demo preview stays in the AI Brief tab |

---

## Tab order

```
🤖 AI Brief  |  🧾 Sales  |  📅 Seasonality  |  🟣 Attribution  |  🟡 Retention  |  🟢 Fulfillment  |  💳 Order Risk  |  🏪 Sellers  |  🚨 Chargeback Risk
```

---

## Tab 1 — 🧾 Sales

**Purpose:** Baseline revenue context before interpreting any other tab.  
**Data:** Synthetic weekly (`wf`, `cf`) · filtered by sidebar period slider.  
**Pillar:** — (neutral)

### KPIs
| Label | Formula |
|---|---|
| Revenue | `sum(shopify_revenue)` |
| Orders | `sum(shopify_orders)` |
| AOV | `Revenue / Orders` |
| Recent vs Start | `(last 4 weeks revenue / first 4 weeks revenue − 1) × 100` |

### Layout
Two columns (3:2).

### Charts
#### 1.1 — Weekly Revenue and Orders
- **Type:** Scatter (line+markers, area fill) + Bar on secondary Y
- **X:** `week_start`
- **Y1:** `shopify_revenue` — line, `#22d3a0`, area fill `rgba(34,211,160,0.08)`
- **Y2:** `shopify_orders` — bars, `rgba(59,158,255,0.28)`, right axis
- **Col:** 1 (wide)

#### 1.2 — Revenue Mix by Category
- **Type:** Donut (Pie, `hole=0.55`)
- **Labels:** top 7 categories by revenue, `_` → space → title case
- **Values:** `sum(revenue)` per category
- **Colors:** `["#22d3a0","#3b9eff","#7c6bff","#f5c542","#9b72cf","#38bdf8","#ff8a4c"]`
- **Col:** 2 (narrow)

### Callout
Default indigo. Shows peak week date, revenue, orders.

---

## Tab 2 — 📅 Seasonality

**Purpose:** Identify repeating demand cycles; plan spend allocation around peaks.  
**Data:** `data/seasonality_monthly.csv`, `data/seasonality_cat_monthly.csv` · Sep 2016–Oct 2018.  
**Pillar:** — (neutral, `#3b9eff`)

### KPIs
| Label | Formula |
|---|---|
| Peak Month | `purchase_month` where `orders` is max |
| Trough Month | `purchase_month` where `orders` is min |
| Peak / Trough | `peak_orders / trough_orders` |
| YoY Growth | `(2018 shared-month orders / 2017 shared-month orders − 1) × 100` |

### Layout
Row 1: full width. Row 2: two columns (1:1). Row 3: full width.

### Charts
#### 2.1 — Monthly Orders with Trend Decomposition
- **Type:** Bar + Scatter line overlay
- **X:** `purchase_month`
- **Y (bar):** `orders` — `rgba(59,158,255,0.4)`
- **Y (line):** `orders.rolling(3, center=True)` — `#3b9eff`, width 2.5, label "Trend (3-mo avg)"
- **Annotation:** peak month labelled with order count, `#f5c542` arrow

#### 2.2 — Seasonal Index by Month (100 = average)
- **Type:** Bar
- **X:** month name (Jan–Dec)
- **Y:** `mean(orders per month_num) / overall_monthly_mean × 100`
- **Color:** `#f5c542` if index ≥ 100 else `#3b9eff`
- **Reference line:** `y=100`, dotted `#2a2a40`
- **Y range:** 50–160
- **Col:** 1

#### 2.3 — Year-over-Year Orders (2016 partial)
- **Type:** Scatter (line+markers), one trace per year
- **X:** month name, fixed category order Jan–Dec
- **Y:** `orders`
- **Colors:** 2016 `#9b72cf` (opacity 0.5), 2017 `#3b9eff`, 2018 `#22d3a0`
- **Col:** 2

#### 2.4 — Which categories drive demand each month — top 5
- **Type:** Stacked Bar
- **X:** `purchase_month`
- **Y:** `orders` per category
- **Colors:** `["#7c6bff","#22d3a0","#f5c542","#3b9eff","#ff8a4c"]`
- **Full width**

### Callout
Default indigo. Explains seasonal index and YoY chart usage.

---

## Tab 3 — 🟣 Attribution

**Purpose:** Prove the attribution problem; offer MER as the honest alternative.  
**Data:** Synthetic weekly (`wf`) · filtered by sidebar period slider.  
**Pillar:** Attribution `#7c6bff`

Three sections separated by `.pillar-section` dividers.

---

### Section 3A — What platforms claim vs what actually happened

**Callout (red):** "~140% of actual revenue claimed by platforms."

#### 3.1 — Weekly Revenue: Shopify Truth vs Platform Claims
- **Type:** Bar + Scatter dotted line
- **X:** `week_start`
- **Y (bar):** `shopify_revenue` — `#22d3a0` (Shopify truth)
- **Y (line):** `total_claimed` — `#ff5566`, dotted, label "Total claimed by platforms"
- **Full width**

#### 3.2 — Platform ROAS cards (3 columns, HTML)
| Card | Background | Primary metric | Secondary |
|---|---|---|---|
| Google Ads | `#0f0f18` | Reported ROAS `{x:.1f}x` in `#3b9eff` | True ROAS `{x:.1f}x` in `#22d3a0` |
| Meta Ads | `#0f0f18` | Reported ROAS `{x:.1f}x` in `#ff6b6b` | True ROAS `{x:.1f}x` in `#22d3a0` |
| Combined Overclaim | `#200a10` | `+{x:.0f}%` in `#ff5566` | BRL claimed vs actual per week + period total |

---

### Section 3B — Revenue per R$1 of ad spend

**Callout (indigo):** MER definition.

#### 3.3 — Weekly MER with Anomaly Detection
- **Type:** Scatter, multi-trace
- **X:** `week_start`
- **Trace 1:** Confidence band — filled area between `mer_baseline ± 1.5×rolling_std(8wk)`, `rgba(124,107,255,0.07)`
- **Trace 2:** `mer_baseline` (8-wk rolling mean) — `#444466`, dotted, 1.5px
- **Trace 3:** `mer` (weekly) — `#7c6bff`, 2px, markers size 3
- **Trace 4:** Anomaly points (`mer` outside ±1.5σ) — `#ff5566`, circle-open, size 9
- **Annotations:** `season_label` where non-empty
- **Col:** 1 (wide, 3:2)

#### 3.4 — Spend Mix by Channel
- **Type:** Stacked Bar
- **X:** `week_start`
- **Traces:** `google_spend` `#3b9eff`, `meta_spend` `#ff6b6b`, `email_cost` `#f5c542`
- **Col:** 2 (narrow)

---

### Section 3C — The GA4 gap

#### 3.5 — Shopify Revenue vs GA4 Tracked Revenue
- **Type:** Dual Scatter area fills
- **X:** `week_start`
- **Y1:** `shopify_revenue` — `#22d3a0`, fill `rgba(34,211,160,0.08)`
- **Y2:** `ga4_revenue` — `#888899`, dashed, fill `rgba(136,136,153,0.06)`
- **Col:** 1 (3:2)

**Callout (col 2, indigo):** 4 reasons for the gap + server-side tracking fix.

---

## Tab 4 — 🟡 Retention

**Purpose:** Show 2.1% repeat rate as the core business problem; surface review quality as a signal.  
**Data:** `data/cohorts_real.csv`, `data/reviews_*.csv` · Sep 2016–Oct 2018.  
**Pillar:** Retention `#f5c542`

Two sections.

---

### Section 4A — Cohort retention & LTV

**Callout (amber):** "2.1% of customers placed a second order within 180 days."

### KPIs
| Label | Formula |
|---|---|
| Total Acquired | `sum(cohort_size)` |
| 180d Repeat Rate | weighted avg `ret_180d` by cohort size |
| Avg LTV (180d) | `mean(ltv_180d)` |
| Low-Retention Cohorts | `sum(is_outlier)` — outlier = `ret_90d < mean − 1.5σ` |

#### 4.1 — Customers who bought again · % who placed a 2nd order within X days
- **Type:** Heatmap
- **Y:** `cohort_month`
- **X:** `["30d","60d","90d","180d"]`
- **Z:** retention % (values × 100), `zmin=0, zmax=8`
- **Colorscale:** `[[0,"#09090e"],[0.3,"#2a1800"],[0.6,"#7a5200"],[1.0,"#f5c542"]]`
- **Annotations:** % value in each cell (9px font)
- **Outlier rows:** red rectangle border + ⚠ annotation (outlier = `ret_90d < mean_90d − 1.5σ`)
- **Col:** 1 (3:2)

#### 4.2 — LTV per Acquired Customer
- **Type:** Scatter (lines)
- **X:** `[30, 60, 90, 180]` (days)
- **Traces:** one per cohort — `#f5c542` opacity 0.25, 0.8px; outlier cohorts `#ff5566` opacity 1.0, 2px
- **Median trace:** `#f5c542`, 2.5px, dashed, markers size 6, shown in legend
- **Col:** 2 (narrow)

---

### Section 4B — Customer review quality

### KPIs
| Label | Formula |
|---|---|
| Total Reviews | `sum(count)` from `reviews_distribution.csv` |
| Avg Score | weighted avg `score × count / total` |
| 5-Star Share | `pct` where `score == 5` |
| 1-Star Share | `pct` where `score == 1` |

#### 4.3 — Score Distribution
- **Type:** Bar
- **X:** `score` as string ("1"–"5")
- **Y:** `count`
- **Colors:** `["#ff2244","#ff6b6b","#f5c542","#3b9eff","#22d3a0"]` (1→5 star)
- **Text:** `pct` formatted as `{v:.1f}%`, outside
- **Col:** 1 (2:3)

#### 4.4 — Score Trend & 1-Star Share
- **Type:** Scatter line + Bar on secondary Y
- **X:** `review_creation_month`
- **Y1 (line):** `avg_score` — `#f5c542`, 2px, markers size 4; range 3.0–5.0
- **Y2 (bar):** `pct_1star` — `rgba(255,34,68,0.30)`, right axis
- **Col:** 2 (wide)

**Callout (red):** Dynamic — lowest-rated category name + score + 1-star %; most 1-star category; best-rated category.

---

## Tab 5 — 🟢 Fulfillment

**Purpose:** Connect delivery lateness to review scores; surface geographic friction.  
**Data:** `data/fulfillment_*.csv`, `data/geo_state_real.csv` · Sep 2016–Oct 2018.  
**Pillar:** Fulfillment `#22d3a0`

Two sections.

---

### Section 5A — Delivery performance

### KPIs
| Label | Formula |
|---|---|
| On-Time Rate | `np.average(on_time_rate, weights=orders)` |
| Avg Delivery | `np.average(avg_delivery_days, weights=orders)` |
| Avg Review Score | `np.average(avg_review_score, weights=orders)` |
| Orders analysed | `sum(orders)` from `fulfillment_by_category.csv` |

#### 5.1 — Review Score vs Delivery Lateness
- **Type:** Bar
- **X:** bucket — `["On time","1–3 days late","4–7 days late","8–14 days late","14+ days late"]`
- **Y:** `avg_score`
- **Colors:** `["#22d3a0","#f5c542","#ff8a4c","#ff6b6b","#ff2244"]` (on-time → worst)
- **Text:** `{v:.2f}★`, outside
- **Hover:** order count from `customdata`
- **Y range:** 1–5.5
- **Col:** 1 (3:2)

**Callout (red):** "On-time = 4.4★. Orders 8–14 days late = ~2.0★. Every late delivery is a review bomb."

#### 5.2 — On-Time Rate & Delivery Speed
- **Type:** Dual-axis Scatter
- **X:** `purchase_month`
- **Y1 (line):** `on_time_rate × 100` — `#22d3a0`, 2px; range 70–100
- **Y2 (dotted):** `avg_delivery_days` — `#38bdf8`, dotted; range 0–40, right axis
- **Col:** 2 (narrow)

**Callout (green):** "Avg delivery improved from ~15 days (2016) to ~9 days (2018) as seller network matured."

---

### Section 5B — Geographic demand & delivery coverage

### KPIs
| Label | Source |
|---|---|
| Top State by Revenue | `state` where `revenue` is max |
| Slowest Delivery | `state` where `avg_delivery_days` is max |
| Highest Late Rate | `state` where `(1 − on_time_rate)` is max |
| Worst Buyer/Seller Ratio | `state` where `customers / seller_count` is max |

#### 5.3 — Revenue by State · colour = late delivery rate
- **Type:** Scattergeo
- **Scope:** South America; center `lat=-14, lon=-52`
- **Lat/Lon:** from `geo_state_real.csv`
- **Size:** log-scaled — `(log1p(revenue) − min) / (max − min) × 36 + 10`
- **Color:** `(1 − on_time_rate) × 100` — `RdYlGn_r` scale, 0–30%
- **Hover:** state, region, revenue, orders, avg delivery, on-time %, review score
- **Col:** 1 (3:2)

#### 5.4 — Avg Delivery Days by State
- **Type:** Horizontal Bar
- **Y:** `state` (top 15 slowest)
- **X:** `avg_delivery_days`
- **Color:** `#ff6b6b` if >20d, `#f5c542` if >12d, else `#22d3a0`
- **Text:** `{v:.1f}d`, auto
- **Col:** 2 (narrow)

**Callout (green):** "Northern/Northeastern states have longest delivery times and fewest sellers. PA = 922 buyers per seller."

---

## Tab 6 — 💳 Order Risk

**Purpose:** Identify payment segments with highest cancellation rates.  
**Data:** `data/payments_by_type.csv`, `data/payments_installments.csv`.  
**Pillar:** — (neutral)

### KPIs
| Label | Formula |
|---|---|
| Credit Card Share | `credit_card orders / total_orders × 100` |
| Boleto Share | `boleto orders / total_orders × 100` |
| Overall Cancel Rate | `total_cancelled / total_orders × 100` |
| Highest-Risk Bucket | `installment_bucket` where `cancellation_rate` is max |

### Layout
Two equal columns.

### Charts

#### 6.1 — Orders & Cancel Rate by Payment Type
- **Type:** Bar + Scatter markers on secondary Y
- **X:** payment type label (Credit Card / Boleto / Voucher / Debit Card)
- **Y1 (bar):** `orders` — `#38bdf8`
- **Y2 (diamond markers):** `cancellation_rate × 100` — `#ff5566`, size 14
- **Col:** 1

#### 6.2 — Orders & Cancel Rate by Installment Count
- **Type:** Bar + Scatter line+markers on secondary Y
- **X:** `installment_bucket` — `["1x","2–3x","4–6x","7–12x","13–24x"]`
- **Y1 (bar):** `orders` — `#9b72cf`
- **Y2 (line):** `cancellation_rate × 100` — `#ff5566`, 2px, markers size 8
- **Col:** 2

**Callout (red):** "13–24x installment orders carry dual risk: payment may not settle + long repayment window."

---

## Tab 7 — 🏪 Sellers

**Purpose:** Surface underperforming sellers; show revenue concentration risk.  
**Data:** `data/seller_performance.csv` (1,238 sellers, ≥10 orders), `data/seller_concentration.csv`.  
**Pillar:** — (neutral)

### KPIs
| Label | Formula |
|---|---|
| Qualifying Sellers | `len(seller_perf)` |
| Top 10 Revenue Share | `top-10 revenue / total revenue × 100` |
| Avg Review Score | `np.average(avg_review_score, weights=orders)` |
| SP Seller Share | `SP orders / total orders × 100` |

### Layout
Two columns (3:2), then full-width expander.

### Charts

#### 7.1 — Revenue vs Review Score (top 200 sellers · colour = on-time rate)
- **Type:** `px.scatter`
- **X:** `revenue`
- **Y:** `avg_review_score`
- **Size:** `orders`, `size_max=30`
- **Color:** `on_time_rate` — `RdYlGn` scale
- **Hover:** `seller_state`, `top_category`, `orders`, `revenue`, `on_time_rate`, `avg_review_score`
- **Col:** 1

#### 7.2 — How many sellers drive 80% of revenue
- **Type:** Scatter line + area fill
- **X:** seller rank (1 → 1,238)
- **Y:** `cumulative_revenue_pct`
- **Line:** `#7c6bff`, 2px; fill `rgba(124,107,255,0.15)`
- **Reference line:** `y=80`, dotted `#f5c542`, annotated "80%"
- **Col:** 2

#### 7.3 — Worst-rated sellers (expander, min 50 orders)
- **Type:** `st.dataframe`
- **Columns:** seller_id (truncated to 12 chars + …), seller_state, top_category, orders, revenue, on_time_rate, avg_review_score
- **Rows:** bottom 12 by `avg_review_score`

---

## Tab 8 — 🚨 Chargeback Risk

**Purpose:** Flag delivered orders most likely to generate chargebacks; quantify revenue at risk by category.  
**Data:** `data/chargeback_monthly.csv`, `data/chargeback_by_category.csv`, `data/chargeback_evidence.csv`.  
**Pillar:** — (red alert)

**Evidence model:** Each delivered order scores 0–3 points:
- `+1` — review score = 1 ★
- `+1` — delivered 7+ days late
- `+1` — max installments ≥ 7

Orders with **score ≥ 2** are flagged.

**Callout (red):** Explains the 3-signal model and the ~80% dispute-loss rate context.

### KPIs
| Label | Formula |
|---|---|
| Flagged Orders | `sum(flagged_orders)` |
| Revenue at Risk | `sum(flagged_revenue)` |
| Flag Rate | `total_flagged / total_delivered × 100` |
| Highest-Risk Category | top row of `chargeback_by_category.csv` by `flag_rate` |

### Layout
Row 1: two columns (3:2). Row 2: two columns (3:2).

### Charts

#### 8.1 — Monthly flagged orders and revenue at risk
- **Type:** Bar + Scatter line on secondary Y
- **X:** `purchase_month`
- **Y1 (bar):** `flagged_orders` — `rgba(255,85,102,0.7)`
- **Y2 (line):** `flagged_revenue` — `#f5c542`, 2px, markers size 5
- **Col:** 1

#### 8.2 — Orders by number of risk signals
- **Type:** Bar
- **X:** label — `["No signals","1 signal","2 signals ⚠","All 3 signals 🚨"]`
- **Y:** `orders`
- **Colors:** `["#2a2a40","#444466","#ff8a4c","#ff5566"]`
- **Hover:** order count + revenue in R$M
- **Col:** 2

#### 8.3 — Flag rate by category (red > 5%, amber > 3%)
- **Type:** Horizontal Bar
- **Y:** top 15 categories by `flag_rate`
- **X:** `flag_rate × 100`
- **Color:** `#ff5566` if >5%, `#ff8a4c` if >3%, else `#f5c542`
- **Hover:** `flagged_revenue` BRL
- **Col:** 1

#### 8.4 — Highest revenue at risk by category (table)
- **Type:** `st.dataframe`
- **Source:** top 8 by `flagged_revenue`
- **Columns:** Category, Revenue at Risk, Flagged Orders, Flag Rate
- **Col:** 2

**Callout (red):** "Categories with high flag rate AND high revenue at risk are priority. Pre-shipment review on flagged orders = highest-ROI first step."

---

## Tab 9 — 🤖 AI Brief

**Purpose:** Demo the packaged AI layer — LLM-generated weekly commerce brief.  
**Data:** Last row of `wf` (synthetic) + OpenAI API (optional).  
**Pillar:** — (neutral)

### KPIs (last week vs prior week)
| Label | Formula |
|---|---|
| MER this week | `last_week.mer` · delta vs prev week |
| Shopify revenue | `last_week.shopify_revenue` · delta WoW % |
| Total spend | `last_week.total_spend` · delta WoW % |
| Overclaim | `last_week.overclaim_pct` |

### Prompt structure
3-paragraph format sent to ChatGPT via OpenAI Responses API, `model="gpt-oss-20b"`, `max_output_tokens=600`, streamed:
1. **What happened** — key growth, attribution, fulfillment, retention, and risk numbers
2. **What it means** — biggest leaks connected to profit or customer experience
3. **First action** — one owner-ready recommendation with a number attached

### Elements
- "Generate Live Brief" primary button → streams response into `.brief-box` div
- Static demo brief shown when no key / not clicked / quota-limited
- Expander: "What the prompt sends to the model" → `st.code(prompt_context)` including the action queue

---

## Data files

| File | Rows | Built by | Used in |
|---|---|---|---|
| `data/fulfillment_review_lateness.csv` | 5 | Section 1 | Tab 5 §A chart 5.1 |
| `data/fulfillment_by_category.csv` | 43 | Section 2 | Tab 5 §A KPIs |
| `data/fulfillment_monthly.csv` | 22 | Section 3 | Tab 5 §A charts 5.2, funnel banner |
| `data/geo_state_real.csv` | 27 | Section 4 | Tab 5 §B charts 5.3–5.4 |
| `data/reviews_distribution.csv` | 5 | Section 5 | Tab 4 §B chart 4.3 |
| `data/reviews_monthly.csv` | 22 | Section 5 | Tab 4 §B chart 4.4 |
| `data/reviews_by_category.csv` | 43 | Section 5 | Tab 4 §B callout |
| `data/payments_by_type.csv` | 4 | Section 6 | Tab 6 chart 6.1 |
| `data/payments_installments.csv` | 5 | Section 6 | Tab 6 chart 6.2 |
| `data/seller_performance.csv` | 1,238 | Section 7 | Tab 7 charts 7.1, 7.3 |
| `data/seller_concentration.csv` | 1,238 | Section 7 | Tab 7 chart 7.2 |
| `data/cohorts_real.csv` | 23 | Section 8 | Tab 4 §A charts 4.1–4.2, funnel banner |
| `data/seasonality_monthly.csv` | 23 | Section 9 | Tab 2 charts 2.1–2.3 |
| `data/seasonality_cat_monthly.csv` | 106 | Section 9 | Tab 2 chart 2.4 |
| `data/chargeback_monthly.csv` | 23 | Section 10 | Tab 8 chart 8.1 |
| `data/chargeback_by_category.csv` | 52 | Section 10 | Tab 8 charts 8.3–8.4 |
| `data/chargeback_evidence.csv` | 4 | Section 10 | Tab 8 chart 8.2 |
| Synthetic (`data_gen.py`) | — | `load_all(seed=42)` | Tabs 1, 3, 9 |

---

## Color reference

| Token | Hex | Used for |
|---|---|---|
| `attribution` | `#7c6bff` | Tab 3 primary, funnel panel 01, MER line, Pareto fill |
| `fulfillment` | `#22d3a0` | Tab 5 primary, on-time trend, Shopify baseline, funnel panel 02 |
| `retention` | `#f5c542` | Tab 4 primary, heatmap highlight, LTV median, funnel panel 03 |
| `claimed` | `#ff5566` | Overclaim indicators, anomaly markers, alert callouts |
| `google` | `#3b9eff` | Google Ads spend traces |
| `meta` | `#ff6b6b` | Meta Ads spend traces |
| `email` | `#f5c542` | Email channel (shares with retention; context makes it clear) |
| `organic` | `#9b72cf` | Organic channel, installment bars |
| `geo` | `#38bdf8` | Geography secondary axis, payment type bars |
| `returns` | `#ff8a4c` | Mid-severity alerts, chargeback amber threshold |
| Background | `#09090e` | App + chart canvas |
| Surface | `#0f0f18` | Cards, sidebar, tab bar |
| Border | `#1c1c2a` | All dividers and borders |
| Text primary | `#eeeeff` | Headings, metric values |
| Text secondary | `#a0a0c0` | Body copy |
| Text muted | `#6060a0` | Labels, axis ticks |
