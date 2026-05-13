# Commerce Leak Studio Outline

**File:** `app.py`  
**Data build:** `python scripts/build_olist_data.py` (run once, outputs to `data/`)  
**Dev server:** `streamlit run app.py`

---

## Product Packaging

| Element | Detail |
|---|---|
| Consultancy | Torm Data Co. |
| Product | Commerce Leak Studio |
| Mock retailer | Luma & Co. |
| Retailer category | Brazilian home, gifts, and lifestyle marketplace |
| Logo | Code-native Luma `L` mark with emerald / amber / indigo gradient |

## Global elements

### Sidebar
- Period slider — filters synthetic weekly data (`wf`, `cf`) only; real Olist tabs show full date range
- Luma & Co. mock retailer brand card
- OpenAI API key — text input used by the top AI panel and AI Brief tab
- Quota-safe demo-mode note for the AI Brief Studio

### Executive snapshot (top of every page, 4 columns)
| Metric | Source | Notes |
|---|---|---|
| Revenue | `wf["shopify_revenue"].sum()` | Filtered by period |
| Spend | `wf["total_spend"].sum()` | |
| MER | Revenue / Spend | delta = recent 5-week change |
| P1 leaks | action queue priority count | owner-action signal |

Platforms claim, GA4 gap, fulfillment, retention, and weeks analysed sit in a secondary expander.

### Funnel / flow banner
Expandable operating-flow panel with three connected stages. Pulls live numbers at render time.

| Panel | Color | Key metric shown |
|---|---|---|
| 01 · Attribution | `#7c6bff` indigo | Spend → Revenue · MER · overclaim % |
| 02 · Fulfillment | `#22d3a0` emerald | On-time rate · orders · avg days |
| 03 · Retention | `#f5c542` amber | 180d repeat rate · customers · LTV |

Fallback text if real data files are absent ("Run build script for live data").

### This Week's Leaks
Top-level action queue beside the AI Brief Studio and above the tabs. Only the top three actions are visible by default; the full queue is expandable.

| Column | Meaning |
|---|---|
| Priority | P1 / P2 |
| Leak | Business issue detected |
| Impact | BRL estimate or proxy |
| Owner | Growth / Ops / Retention / Finance / Marketplace Ops |
| Recommended action | One concrete next step |
| Confidence | High / Medium |
| Source | Underlying dashboard data source |

Includes platform overclaim, late delivery exposure, low repeat purchase, chargeback risk, installment cancellation risk, and seller quality drag.

### Data trust
Expandable source coverage table showing which synthetic and real generated datasets are available and when the real files were last built.

### AI Brief Studio
Prominent panel beside the action queue and above the tabs.

| Element | Detail |
|---|---|
| Button | Generate AI Brief |
| Live mode | Streams from OpenAI Responses API using `gpt-oss-20b` and the dashboard prompt |
| Demo mode | Keeps a polished brief preview available without API usage |
| Quota mode | Catches quota, rate-limit, and billing errors and falls back to demo output |

---

## Pillar color system

| Pillar | Hex | Used in tabs |
|---|---|---|
| Attribution | `#7c6bff` | 🟣 Attribution |
| Fulfillment | `#22d3a0` | 🟢 Fulfillment |
| Retention | `#f5c542` | 🟡 Retention |
| Neutral | `#3b9eff` | 🧾 Sales, 📅 Seasonality |

CSS callout variants: `.callout` (default indigo), `.callout-red`, `.callout-green`, `.callout-amber`

---

## Tabs

### 🧾 Sales
**Data:** Synthetic weekly (`wf`, `cf`)  
**Purpose:** Baseline context before interpreting any attribution, retention, or geo data.

**KPIs (4):** Revenue · Orders · AOV · Recent vs Start %

**Charts:**

| # | Type | X | Y | Color | Key insight |
|---|---|---|---|---|---|
| 1 | Line + Bar (dual axis) | Week | Revenue / Orders | `#22d3a0` / blue | Weekly trend; spot peaks |
| 2 | Donut | — | Revenue by category | 7-color palette | Top-7 category revenue mix |

**Callout:** Peak week date, revenue, orders, top category.

---

### 📅 Seasonality
**Data:** Real Olist `data/seasonality_monthly.csv`, `data/seasonality_cat_monthly.csv`  
**Purpose:** Show repeating demand cycles, month-of-year patterns, YoY comparison.

**KPIs (4):** Peak Month · Trough Month · Peak/Trough ratio · YoY growth (2018 vs 2017)

**Charts:**

| # | Type | Description | Color |
|---|---|---|---|
| 1 | Bar + 2 lines | Monthly orders · 3-mo rolling avg · 6-mo rolling avg · peak annotation | `#3b9eff` |
| 2 | Bar | Seasonal index per calendar month (100 = baseline) | Amber ≥100, blue <100 |
| 3 | Multi-line | Year-over-year orders: 2016 (partial), 2017, 2018 on shared month axis | Purple/blue/green per year |
| 4 | Bar (diverging) | Detrended seasonal component (actual − trend); green above, red below | Green / red |
| 5 | Stacked bar | Top 5 categories monthly order mix | 5-color pillar palette |

**Callout:** Explains seasonal index and detrended chart usage.

---

### 🟣 Attribution
**Data:** Synthetic weekly (`wf`)  
**Purpose:** Show the attribution problem: platform overclaiming, MER as truth, GA4 gap.  
**Pillar color:** `#7c6bff` indigo

Three sections separated by `.pillar-section` dividers:

#### Section 1 — The Attribution Lie
**Callout (red):** "Platforms collectively claim ~140% of actual revenue."

| # | Type | Description |
|---|---|---|
| 1 | Bar + dotted line | Weekly Shopify truth (bars) vs total platform claims (line) |

**ROAS cards (3 columns):**
- Google: reported ROAS vs true ROAS + overclaim %
- Meta: reported ROAS vs true ROAS + overclaim %
- Combined: total overclaim %, phantom revenue BRL

#### Section 2 — MER Reality
**Callout (indigo):** MER definition, why it sidesteps attribution.

| # | Type | Description |
|---|---|---|
| 2 | Line + band | Weekly MER · 8-wk rolling baseline · ±1.5σ confidence band · anomaly markers · season labels |
| 3 | Stacked bar | Weekly spend by channel: Google / Meta / Email |

#### Section 3 — GA4 Gap
| # | Type | Description |
|---|---|---|
| 4 | Dual area line | Shopify revenue vs GA4-tracked revenue weekly |

**Callout:** 4 reasons for the gap (ad blockers, iOS ITP, payment redirects, Shopify Checkout). Fix: server-side GTM + CAPI + Enhanced Conversions.

---

### 🟢 Fulfillment
**Data:** Real Olist  
**Purpose:** Connect delivery lateness to review scores; show geographic delivery friction.  
**Pillar color:** `#22d3a0` emerald

Two sections:

#### Section 1 — Delivery SLA
**KPIs (4):** On-Time Rate · Avg Delivery · Avg Review Score · Orders Analysed

| # | Type | Data | Color | Key insight |
|---|---|---|---|---|
| 1 | Bar | Review score per lateness bucket (On time / 1–3d / 4–7d / 8–14d / 14+d) | Emerald→red gradient | On-time = 4.4★; 8–14d late = ~2.0★ |
| 2 | Dual-axis line | Monthly on-time % + avg delivery days | Emerald / teal dotted | Delivery improved 15d→9d from 2016 to 2018 |

**Callouts:** "Every late delivery is a review bomb." + delivery speed improvement trend.

#### Section 2 — Geography
**KPIs (4):** Top State Revenue · Slowest Delivery State · Highest Late Rate State · Worst Buyer/Seller Ratio State

| # | Type | Data | Key insight |
|---|---|---|---|
| 3 | Bubble map (Brazil) | Size = log(revenue), color = late delivery % | North/Northeast = slow + low review |
| 4 | Horizontal bar | Avg delivery days by state, top 15 | Color: red >20d, amber >12d, green ≤12d |

**Callout (green):** PA has 922 buyers per seller — most underserved market.

---

### 🟡 Retention
**Data:** Real Olist  
**Purpose:** Show near-zero repeat purchase, low LTV, and review quality by category.  
**Pillar color:** `#f5c542` amber

Two sections:

#### Section 1 — Cohort Retention & LTV
**KPIs (4):** Total Acquired · 180d Repeat Rate · Avg LTV (180d) · Outlier Cohorts

**Callout (amber):** "2.1% of customers placed a second order within 180 days."

| # | Type | Data | Color | Key insight |
|---|---|---|---|---|
| 1 | Heatmap | Cohort × period (30/60/90/180d), 0–8% color scale | Dark→amber | Near-zero retention across all cohorts |
| 2 | Multi-line | LTV curves per cohort; red = statistical outlier (>1.5σ below mean 90d retention) | Amber / red outliers | Flat LTV — acquisition not compounding |
| 3 | Bar | New customers acquired per month | Amber | Growth trend in customer volume |

Outlier detection: `ret_90d < mean_90d − 1.5 * std_90d` → red border on heatmap row + ⚠ label.

#### Section 2 — Review Quality
**KPIs (4):** Total Reviews · Avg Score · 5-Star Share · 1-Star Share

| # | Type | Data | Key insight |
|---|---|---|---|
| 4 | Bar | Score distribution 1–5 | 55% five-star, 11% one-star; bimodal |
| 5 | Dual-axis line | Monthly avg score + 1-star % as bar | Trend + volume of dissatisfaction |

**Callout (red):** Lowest-rated category, most 1-star category, best-rated category (dynamic from data).

---

### 💳 Order Risk
**Data:** Real Olist `data/payments_by_type.csv`, `data/payments_installments.csv`  
**Purpose:** Identify high-cancellation payment segments.

**KPIs (4):** Credit Card Share · Boleto Share · Overall Cancel Rate · Highest-Risk Bucket

| # | Type | Data | Key insight |
|---|---|---|---|
| 1 | Bar + diamond markers (dual axis) | Orders + cancel rate per payment type | Boleto cancels at higher rate than credit card |
| 2 | Bar + line (dual axis) | Orders + cancel rate per installment bucket (1x / 2–3x / 4–6x / 7–12x / 13–24x) | 13–24x installments = highest cancel rate |

**Callout (red):** High-installment boleto = dual risk (unsettled payment + long repayment).

---

### 🏪 Sellers
**Data:** Real Olist `data/seller_performance.csv`, `data/seller_concentration.csv`  
**Purpose:** Surface underperforming sellers and revenue concentration risk.

**KPIs (4):** Qualifying Sellers · Top 10 Revenue Share · Avg Review Score · SP Seller Share

| # | Type | Data | Key insight |
|---|---|---|---|
| 1 | Scatter | Revenue vs review score (top 200 sellers), size = orders, color = on-time rate (RdYlGn) | High-revenue sellers with poor quality visible |
| 2 | Area line | Pareto — cumulative revenue % vs seller rank | 80% line annotated in amber |

**Expander:** Worst-rated sellers table (min 50 orders) — seller_id (truncated), state, category, orders, revenue, on-time %, avg review.

---

### 🤖 AI Brief
**Data:** Last week from `wf`; streams from OpenAI API  
**Purpose:** Demo the product: LLM-generated weekly commerce brief.

**KPIs (4):** MER this week (vs prev) · Shopify revenue (WoW %) · Total spend (WoW %) · Overclaim %

**Prompt structure:** 3-paragraph format — What happened · What it means · First action. Includes attribution metrics, operations context, risk context, and the prioritized action queue.  
Model: `gpt-oss-20b`, `max_output_tokens=600`, streamed through the OpenAI Responses API.

**Static demo** shown when no key, no click, or quota is unavailable.  
**Expander:** Full prompt context displayed as code block.

---

## Data sources

| File | Rows | Contents | Used by |
|---|---|---|---|
| `data/fulfillment_review_lateness.csv` | 5 | Avg review score per lateness bucket | Fulfillment §1 |
| `data/fulfillment_by_category.csv` | 43 | On-time rate, days, review, revenue per category | (available, not currently charted) |
| `data/fulfillment_monthly.csv` | 22 | Monthly on-time %, avg days, avg review, orders | Fulfillment §1, funnel banner |
| `data/geo_state_real.csv` | 27 | Revenue, orders, customers, sellers, delivery per BR state | Fulfillment §2 |
| `data/reviews_distribution.csv` | 5 | Score 1–5 count + % | Retention §2 |
| `data/reviews_monthly.csv` | 22 | Monthly avg score, 1-star %, 5-star % | Retention §2 |
| `data/reviews_by_category.csv` | 43 | Avg score, 1-star %, orders per category | Retention §2 callout |
| `data/payments_by_type.csv` | 4 | Orders, cancel rate, avg value per payment type | Order Risk |
| `data/payments_installments.csv` | 5 | Orders, cancel rate, avg value per installment bucket | Order Risk |
| `data/seller_performance.csv` | 1,238 | Revenue, orders, on-time, review, state, top category per seller | Sellers |
| `data/seller_concentration.csv` | 1,238 | Cumulative revenue % (Pareto) | Sellers |
| `data/cohorts_real.csv` | 23 | Retention (30/60/90/180d) and LTV per monthly cohort | Retention §1, funnel banner |
| `data/seasonality_monthly.csv` | 23 | Monthly orders, revenue, review, on-time, year, month_num | Seasonality |
| `data/seasonality_cat_monthly.csv` | 106 | Orders per month per top-5 category | Seasonality |
| Synthetic (`data_gen.py`) | — | Weekly attribution, MER, GA4 data | Sales, Attribution, AI Brief |

---

## Things not yet built (from PROCESS.md)

- [ ] **Chargeback risk tab** — flag 1★ + late + high-installment orders as dispute proxies; show projected monthly loss
- [ ] **Cart abandonment proxy** — `order_status = cancelled/unavailable` + payment type as session-less signal
- [ ] **Seller performance tab expansion** — on-time trend per seller over time
- [ ] **Connect real channel data** — replace synthetic attribution with live Shopify + Meta UTM export
