# Retail Intelligence — Casa Viva

> A profit-leak dashboard and AI agent framework for Brazilian e-commerce, built with real Olist data and packaged as a **Torm Studio** product.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?logo=streamlit&logoColor=white)
![DuckDB](https://img.shields.io/badge/DuckDB-analytics-FFF000?logo=duckdb&logoColor=black)
![OpenAI](https://img.shields.io/badge/OpenAI-gpt--4o--mini-412991?logo=openai&logoColor=white)

---

## What it does

The dashboard surfaces profit leaks across marketing, fulfillment, retention, payments, sellers, and chargeback risk for **Casa Viva**, a mock Brazilian home, gifts, and lifestyle marketplace.

The main output is an **owner-ready opportunity queue** with impact estimates and recommended actions — modeled on real Olist e-commerce data plus synthetic attribution and returns signals.

---

## Dashboard sections

| Section | What you see |
| --- | --- |
| **Executive Brief** | Spend, delivery, repeat purchase, and the next best action in one operating view |
| **Revenue** | Shopify revenue, orders, AOV, weekly trend, and category mix |
| **Categories** | Category growth, returns, refund value, return reasons, and health scores |
| **Demand** | Monthly cycles, seasonal index, YoY order trends, and demand mix |
| **Attribution** | Platform-reported revenue vs Shopify truth, MER anomalies, spend mix, and GA4 gaps |
| **Retention** | Cohort repeat rates, LTV curves, review distribution, and category review quality |
| **Fulfillment** | Delivery lateness, on-time rate, review impact, and geographic coverage |
| **Payments** | Payment mix, installment cancellation risk, and payment patterns by category/state |
| **Sellers** | Seller quality, revenue concentration, and sellers with revenue at risk |
| **Risk** | Chargeback proxy flags, monthly exposure, and category risk rates |
| **Agent Prototypes** | Automation concepts tied to the dashboard's highest-value leaks |
| **AI Brief Studio** | Optional OpenAI-powered brief generation from the live opportunity queue |

---

## AI agent prototypes

7 agents model **R$1.1M+ in total identified opportunity**. Each agent watches specific dashboard sections and produces an operational action — not another report.

| Agent | Watches | Problem caught | Action | Opportunity |
| --- | --- | --- | --- | --- |
| **Chargeback Triage** | Risk, Categories | Suspicious order patterns ship before dispute signals are reviewed | Create Finance ticket; flag sellers for pre-shipment review | R$420k at-risk orders/year |
| **Repeat Customer Detector** | Retention, Fulfillment | A bad delivery month suppresses cohort repeat purchases | Queue recovery emails and gift cards for affected customers | R$38k+ lost repeats/bad month |
| **Budget Reallocation Advisor** | Attribution, Categories, Retention | Quarterly spend planning ignores fraud, delivery quality, and LTV | Draft Growth/Finance reallocation ticket with category scores | R$22k projected LTV uplift/planning cycle |
| **Seller Health Monitor** | Sellers, Fulfillment | Seller SLA breaches accumulate before Marketplace Ops intervenes | Send seller warning; open Marketplace Ops follow-up | R$197k seller revenue protected/year |
| **Review Crisis Responder** | Categories, Fulfillment | A 1-star review spike is misread before root cause is traced | Email affected customers, issue vouchers, escalate cause | R$85k at-risk revenue/bad-review wave |
| **Geo Expansion Scout** | Fulfillment, Categories | High-demand states have too few local sellers and slower delivery | Create Partnerships recruitment brief by state | R$210k annual revenue/top underserved state |
| **Manufacturer Escalation** | Categories, Retention | Product defects are mistaken for fulfillment issues | Send manufacturer evidence pack; open category audit ticket | R$130k quality-driven churn/affected category |

---

## Run locally

```bash
pip install -r requirements.txt
python scripts/build_olist_data.py
streamlit run app.py
```

> [!NOTE]
> The build step converts Olist CSV inputs into local parquet datasets. If you skip it, the app still opens with synthetic attribution and category data — but Olist-backed views will be limited.

---

## Deploy

Deploy on **Streamlit Community Cloud** with `app.py` as the main file.

Add `OPENAI_API_KEY` in Streamlit secrets to enable live brief generation. Without it, the built-in demo brief is shown instead.

See [DEPLOY.md](DEPLOY.md) for GitHub, Streamlit Cloud, and GoDaddy/static landing-page notes.

---

## Data sources

| Signal | Source |
| --- | --- |
| Fulfillment, reviews, payments, sellers, geography | Real Olist dataset |
| Spend attribution, platform overclaim, GA4 gaps | Synthetic |
| Revenue mix and returns | Synthetic, modeled to match the dashboard story |

No real customer data is included.

---

## Project layout

```text
app.py                        Streamlit routing, loading, filters, opportunity queue
shared.py                     Shared formatting, chart, and OpenAI helpers
views/                        One render module per dashboard section
data_gen.py                   Synthetic weekly/category/return data
scripts/build_olist_data.py   Olist CSV → parquet build pipeline
```

**Stack:** Streamlit · pandas · DuckDB · Plotly · OpenAI `gpt-4o-mini`
