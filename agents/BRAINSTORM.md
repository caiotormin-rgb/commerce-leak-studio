# Agentic Automation Use Cases — Retail Intelligence

Brainstormed 2026-05-13. Based on the synthetic Olist Brazil retail dataset.

---

## Dataset Coverage

| Domain | Key Files |
|---|---|
| Fulfillment | `fulfillment_monthly.csv`, `fulfillment_by_category.csv`, `fulfillment_review_lateness.csv` |
| Chargebacks / Fraud | `chargeback_monthly.csv`, `chargeback_by_category.csv`, `chargeback_evidence.csv` |
| Reviews | `reviews_monthly.csv`, `reviews_by_category.csv`, `reviews_distribution.csv` |
| Cohorts / Retention | `cohorts_real.csv` |
| Sellers | `seller_performance.csv`, `seller_concentration.csv` |
| Payments | `payments_by_type.csv`, `payments_installments.csv` |
| Geo | `geo_state_real.csv` |
| Seasonality | `seasonality_monthly.csv`, `seasonality_cat_monthly.csv` |

---

## Prototype Ideas

### 1. Seller Health Monitor Agent
**Trigger:** Nightly scheduled run  
**What it does:** Scans `seller_performance` and flags sellers whose `on_time_rate` or `avg_review_score` drops below threshold. Drafts a templated alert (email or Slack) with the specific metrics and delta.  
**Why it's agentic:** Multi-step — diagnose which metric triggered, compose a context-aware message, decide severity level.  
**Business value:** Seller degradation is a slow bleed; early intervention recovers revenue quietly.

---

### 2. Chargeback Triage Agent
**Trigger:** Weekly scheduled run  
**What it does:** Reads `chargeback_by_category` + `chargeback_monthly`, ranks categories by `flag_rate` delta vs. prior period, and generates a structured risk report with recommended actions (hold payments, flag sellers in category).  
**Why it's agentic:** Requires trend reasoning across time, not just threshold comparison. Output is a decision brief.  
**Business value:** Proactive fraud containment before it hits reconciliation.

---

### 3. Cohort LTV Anomaly Agent
**Trigger:** Monthly run after cohort refresh  
**What it does:** Detects cohorts where 30→90-day retention decay is steeper than peers. Cross-references `fulfillment_monthly` and `reviews_monthly` from the same cohort period to hypothesize root causes.  
**Why it's agentic:** Cross-table causal reasoning — this is where single-query BI fails and agents shine.  
**Business value:** Connects retention drops to operational failures, enabling targeted fixes.

---

### 4. Category Reallocation Advisor
**Trigger:** On-demand, given a budget constraint as input  
**What it does:** Synthesizes review scores, on-time rates, chargeback risk, and cohort LTV to rank categories for increased/decreased marketing investment. Returns a ranked recommendation with trade-off rationale.  
**Why it's agentic:** Multi-signal synthesis + constraint satisfaction. Decision output, not data output.  
**Business value:** Replaces analyst hours for quarterly budget planning.

---

### 5. Geo Expansion Scout
**Trigger:** On-demand or quarterly  
**What it does:** Ranks states by untapped potential — high order volume but low `seller_count` or poor `on_time_rate` — and generates a one-page market opportunity brief per candidate state.  
**Why it's agentic:** Combines `geo_state_real` with `seller_concentration`. Produces a narrative artifact, not a dashboard metric.  
**Business value:** Data-driven seller recruitment targeting.

---

### 6. Review Crisis Responder
**Trigger:** Event-driven — when 1-star rate spikes month-over-month  
**What it does:** Detects spike in `reviews_by_category`, cross-references `fulfillment_review_lateness` for causal signal, produces a root-cause summary and escalation recommendation.  
**Why it's agentic:** Reactive + causal chain reasoning. Demonstrates event-triggered vs. scheduled behavior.  
**Business value:** Faster response loop on reputation damage.

---

## Prioritization

| Prototype | Complexity | Demo Impact | Recommended Order |
|---|---|---|---|
| Chargeback Triage Agent | Low | Medium | **1st** |
| Cohort LTV Anomaly Agent | Medium | High | **2nd** |
| Category Reallocation Advisor | Medium | Very High | **3rd** |
| Seller Health Monitor | Low | Medium | 4th |
| Review Crisis Responder | Medium | Medium | 5th |
| Geo Expansion Scout | Low | Medium | 6th |

**Start with Chargeback Triage** — single table pair, clear output, easy to evaluate correctness.  
**Best stakeholder demo: Category Reallocation Advisor** — most obviously replaces analyst work.
