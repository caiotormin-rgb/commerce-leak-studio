#!/usr/bin/env python3
"""
Pre-aggregate real Olist CSVs into dashboard-ready files.

Run once (or after updating source files):
    python scripts/build_olist_data.py

Outputs to data/:
    fulfillment_review_lateness.csv   — avg review score per delivery-lateness bucket
    fulfillment_by_category.csv       — on-time rate, delivery days, review score by category
    fulfillment_monthly.csv           — monthly trend of on-time rate and delivery speed
    geo_state_real.csv                — revenue, orders, delivery performance by BR state
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).parent.parent
SRC  = ROOT / "files"
OUT  = ROOT / "data"
OUT.mkdir(exist_ok=True)

# ── Load ───────────────────────────────────────────────────────────────────
print("Loading CSVs…")
orders = pd.read_csv(
    SRC / "olist_orders_dataset.csv",
    parse_dates=[
        "order_purchase_timestamp",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
)
items     = pd.read_csv(SRC / "olist_order_items_dataset.csv")
products  = pd.read_csv(SRC / "olist_products_dataset.csv")
cat_trans = pd.read_csv(SRC / "product_category_name_translation.csv")
customers = pd.read_csv(SRC / "olist_customers_dataset.csv")
reviews   = pd.read_csv(SRC / "olist_order_reviews_dataset.csv")
sellers   = pd.read_csv(SRC / "olist_sellers_dataset.csv")
geo_raw   = pd.read_csv(SRC / "olist_geolocation_dataset.csv")

# ── Build master order table ───────────────────────────────────────────────
print("Joining tables…")

# English product category per order (mode of items in order)
products = products.merge(cat_trans, on="product_category_name", how="left")
products["category"] = (
    products["product_category_name_english"]
    .fillna(products["product_category_name"])
    .str.replace("_", " ")
    .str.title()
)
items_cat = items.merge(products[["product_id", "category"]], on="product_id", how="left")
def _mode_or_other(x):
    m = x.dropna().mode()
    return m.iloc[0] if len(m) > 0 else "Other"

order_category = (
    items_cat.groupby("order_id")["category"]
    .agg(_mode_or_other)
    .reset_index()
    .rename(columns={"category": "primary_category"})
)

# Revenue per order
order_revenue = (
    items.groupby("order_id")["price"]
    .sum()
    .reset_index()
    .rename(columns={"price": "revenue"})
)

# Mean review score per order
order_reviews = reviews.groupby("order_id")["review_score"].mean().reset_index()

# Master join
master = (
    orders
    .merge(order_revenue,   on="order_id", how="left")
    .merge(order_category,  on="order_id", how="left")
    .merge(
        customers[["customer_id", "customer_unique_id", "customer_state"]],
        on="customer_id", how="left",
    )
    .merge(order_reviews, on="order_id", how="left")
)

# Delivery metrics
has_dates = (
    master["order_delivered_customer_date"].notna()
    & master["order_estimated_delivery_date"].notna()
)
master["delivered_on_time"] = np.where(
    has_dates,
    master["order_delivered_customer_date"] <= master["order_estimated_delivery_date"],
    np.nan,
)
master["delivery_days"] = (
    master["order_delivered_customer_date"] - master["order_purchase_timestamp"]
).dt.days
master["days_late"] = np.maximum(
    0,
    (master["order_delivered_customer_date"] - master["order_estimated_delivery_date"])
    .dt.days.fillna(0),
)
master["purchase_month"] = master["order_purchase_timestamp"].dt.strftime("%Y-%m")

delivered = master[master["order_status"] == "delivered"].copy()
print(f"  Delivered orders: {len(delivered):,}")

# ── 1. Review score × delivery lateness ───────────────────────────────────
delivered["days_late_bucket"] = pd.cut(
    delivered["days_late"],
    bins=[-0.1, 0, 3, 7, 14, 9999],
    labels=["On time", "1–3 days late", "4–7 days late", "8–14 days late", "14+ days late"],
)
review_lateness = (
    delivered.groupby("days_late_bucket", observed=True)["review_score"]
    .agg(avg_score="mean", order_count="count")
    .reset_index()
    .rename(columns={"days_late_bucket": "bucket"})
)
review_lateness.to_csv(OUT / "fulfillment_review_lateness.csv", index=False)
print(f"  fulfillment_review_lateness.csv  ({len(review_lateness)} rows)")

# ── 2. Fulfillment by category ─────────────────────────────────────────────
by_cat = (
    delivered.groupby("primary_category")
    .agg(
        orders           = ("order_id",          "count"),
        on_time_rate     = ("delivered_on_time",  "mean"),
        avg_delivery_days= ("delivery_days",      "mean"),
        avg_review_score = ("review_score",       "mean"),
        avg_days_late    = ("days_late",          "mean"),
        revenue          = ("revenue",            "sum"),
    )
    .reset_index()
    .dropna(subset=["on_time_rate", "avg_review_score"])
)
by_cat = by_cat[by_cat["orders"] >= 200].copy()
by_cat.to_csv(OUT / "fulfillment_by_category.csv", index=False)
print(f"  fulfillment_by_category.csv      ({len(by_cat)} rows)")

# ── 3. Monthly fulfillment trend ───────────────────────────────────────────
monthly = (
    delivered.groupby("purchase_month")
    .agg(
        orders           = ("order_id",         "count"),
        on_time_rate     = ("delivered_on_time", "mean"),
        avg_delivery_days= ("delivery_days",     "mean"),
        avg_review_score = ("review_score",      "mean"),
    )
    .reset_index()
)
# Drop the last month (usually partial)
monthly = monthly.iloc[:-1]
monthly.to_csv(OUT / "fulfillment_monthly.csv", index=False)
print(f"  fulfillment_monthly.csv          ({len(monthly)} rows)")

# ── 4. Geo state summary ───────────────────────────────────────────────────
state_centroids = (
    geo_raw.groupby("geolocation_state")
    .agg(lat=("geolocation_lat", "mean"), lon=("geolocation_lng", "mean"))
    .reset_index()
    .rename(columns={"geolocation_state": "state"})
)
seller_count = (
    sellers.groupby("seller_state")
    .size()
    .reset_index(name="seller_count")
    .rename(columns={"seller_state": "state"})
)

by_state = (
    delivered.groupby("customer_state")
    .agg(
        orders            = ("order_id",          "count"),
        revenue           = ("revenue",           "sum"),
        customers         = ("customer_unique_id", "nunique"),
        on_time_rate      = ("delivered_on_time",  "mean"),
        avg_delivery_days = ("delivery_days",      "mean"),
        avg_review_score  = ("review_score",       "mean"),
    )
    .reset_index()
    .rename(columns={"customer_state": "state"})
)
by_state = (
    by_state
    .merge(state_centroids, on="state", how="left")
    .merge(seller_count,    on="state", how="left")
)
by_state["seller_count"] = by_state["seller_count"].fillna(0).astype(int)

# BR region mapping
REGIONS = {
    "SP": "Southeast", "RJ": "Southeast", "MG": "Southeast", "ES": "Southeast",
    "RS": "South",     "PR": "South",     "SC": "South",
    "BA": "Northeast", "PE": "Northeast", "CE": "Northeast", "MA": "Northeast",
    "PA": "Northeast", "PB": "Northeast", "RN": "Northeast", "SE": "Northeast",
    "AL": "Northeast", "PI": "Northeast",
    "DF": "Central-West", "GO": "Central-West", "MT": "Central-West", "MS": "Central-West",
    "AM": "North",  "PA": "North",  "RO": "North",  "AC": "North",
    "RR": "North",  "AP": "North",  "TO": "North",
}
by_state["region"] = by_state["state"].map(REGIONS).fillna("Other")
by_state.to_csv(OUT / "geo_state_real.csv", index=False)
print(f"  geo_state_real.csv               ({len(by_state)} rows)")

# ── 5. Reviews ────────────────────────────────────────────────────────────────
print("Building review aggregations…")

reviews_df = reviews.copy()
reviews_df["review_creation_month"] = pd.to_datetime(
    reviews_df["review_creation_date"]
).dt.strftime("%Y-%m")

# Score distribution
score_dist = (
    reviews_df["review_score"].value_counts()
    .reset_index()
    .rename(columns={"review_score": "score", "count": "count"})
    .sort_values("score")
)
score_dist["pct"] = score_dist["count"] / len(reviews_df) * 100
score_dist.to_csv(OUT / "reviews_distribution.csv", index=False)

# Monthly trend
monthly_reviews = (
    reviews_df.groupby("review_creation_month")
    .agg(
        review_count  = ("review_id",     "count"),
        avg_score     = ("review_score",  "mean"),
        pct_1star     = ("review_score",  lambda x: (x == 1).mean() * 100),
        pct_5star     = ("review_score",  lambda x: (x == 5).mean() * 100),
    )
    .reset_index()
    .iloc[:-1]   # drop partial last month
)
monthly_reviews.to_csv(OUT / "reviews_monthly.csv", index=False)

# By category: delivered already has review_score from master join
reviews_by_cat = (
    delivered.rename(columns={"review_score": "review_score"})
    .groupby("primary_category")
    .agg(
        orders       = ("order_id",     "count"),
        review_count = ("review_score", "count"),
        avg_score    = ("review_score", "mean"),
        pct_1star    = ("review_score", lambda x: (x == 1).mean() * 100),
        pct_5star    = ("review_score", lambda x: (x == 5).mean() * 100),
    )
    .reset_index()
    .dropna(subset=["avg_score"])
)
reviews_by_cat = reviews_by_cat[reviews_by_cat["orders"] >= 200]
reviews_by_cat.to_csv(OUT / "reviews_by_category.csv", index=False)

print(f"  reviews_distribution.csv         ({len(score_dist)} rows)")
print(f"  reviews_monthly.csv              ({len(monthly_reviews)} rows)")
print(f"  reviews_by_category.csv          ({len(reviews_by_cat)} rows)")

# ── 6. Payments & order risk ───────────────────────────────────────────────────
print("Building payment aggregations…")

payments_df = pd.read_csv(SRC / "olist_order_payments_dataset.csv")

order_pay = (
    payments_df.groupby("order_id")
    .agg(
        payment_type     = ("payment_type",        lambda x: x.mode().iloc[0]),
        max_installments = ("payment_installments", "max"),
        total_payment    = ("payment_value",        "sum"),
    )
    .reset_index()
)

pay_master = master.merge(order_pay, on="order_id", how="left")
pay_master["is_cancelled"] = pay_master["order_status"].isin(["cancelled", "unavailable"])

by_pay_type = (
    pay_master[pay_master["payment_type"] != "not_defined"]
    .groupby("payment_type")
    .agg(
        orders            = ("order_id",          "count"),
        revenue           = ("revenue",           "sum"),
        cancelled         = ("is_cancelled",      "sum"),
        avg_installments  = ("max_installments",  "mean"),
        avg_value         = ("total_payment",     "mean"),
    )
    .reset_index()
)
by_pay_type["cancellation_rate"] = by_pay_type["cancelled"] / by_pay_type["orders"]
by_pay_type.to_csv(OUT / "payments_by_type.csv", index=False)

BUCKET_ORDER = ["1x", "2–3x", "4–6x", "7–12x", "13–24x"]

def _installment_bucket(n):
    n = int(n) if not np.isnan(n) else 1
    if n <= 1:  return "1x"
    if n <= 3:  return "2–3x"
    if n <= 6:  return "4–6x"
    if n <= 12: return "7–12x"
    return "13–24x"

pay_master["installment_bucket"] = pay_master["max_installments"].fillna(1).map(_installment_bucket)
by_installments = (
    pay_master.groupby("installment_bucket")
    .agg(
        orders            = ("order_id",         "count"),
        cancelled         = ("is_cancelled",     "sum"),
        avg_value         = ("total_payment",    "mean"),
        avg_review_score  = ("review_score",     "mean"),
    )
    .reset_index()
)
by_installments["cancellation_rate"] = by_installments["cancelled"] / by_installments["orders"]
by_installments["_ord"] = by_installments["installment_bucket"].map(
    {b: i for i, b in enumerate(BUCKET_ORDER)}
)
by_installments = by_installments.sort_values("_ord").drop("_ord", axis=1)
by_installments.to_csv(OUT / "payments_installments.csv", index=False)

print(f"  payments_by_type.csv             ({len(by_pay_type)} rows)")
print(f"  payments_installments.csv        ({len(by_installments)} rows)")

# ── 7. Seller performance ──────────────────────────────────────────────────────
print("Building seller aggregations…")

items_enriched = (
    items
    .merge(master[["order_id", "delivered_on_time", "review_score",
                   "delivery_days", "order_status"]], on="order_id", how="left")
    .merge(sellers[["seller_id", "seller_state"]],   on="seller_id",  how="left")
    .merge(products[["product_id", "category"]],     on="product_id", how="left")
)
items_delivered = items_enriched[items_enriched["order_status"] == "delivered"]

seller_perf = (
    items_delivered.groupby("seller_id")
    .agg(
        revenue           = ("price",             "sum"),
        orders            = ("order_id",          "nunique"),
        items             = ("order_item_id",     "count"),
        on_time_rate      = ("delivered_on_time", "mean"),
        avg_review_score  = ("review_score",      "mean"),
        avg_delivery_days = ("delivery_days",     "mean"),
        seller_state      = ("seller_state",      "first"),
    )
    .reset_index()
)

seller_top_cat = (
    items_delivered.groupby("seller_id")["category"]
    .agg(_mode_or_other)
    .reset_index()
    .rename(columns={"category": "top_category"})
)
seller_perf = (
    seller_perf
    .merge(seller_top_cat, on="seller_id", how="left")
    .dropna(subset=["on_time_rate", "avg_review_score"])
)
seller_perf = seller_perf[seller_perf["orders"] >= 10].sort_values("revenue", ascending=False)
seller_perf.to_csv(OUT / "seller_performance.csv", index=False)

# Revenue concentration stats
total_rev = seller_perf["revenue"].sum()
seller_perf_sorted = seller_perf.sort_values("revenue", ascending=False).reset_index(drop=True)
seller_perf_sorted["cumulative_revenue_pct"] = (
    seller_perf_sorted["revenue"].cumsum() / total_rev * 100
)
seller_perf_sorted.to_csv(OUT / "seller_concentration.csv", index=False)

print(f"  seller_performance.csv           ({len(seller_perf)} rows)")
print(f"  seller_concentration.csv         ({len(seller_perf_sorted)} rows)")

# ── 8. Cohorts (real repeat retention) ────────────────────────────────────────
print("Building cohort data…")

cohort_base = (
    master[master["order_status"] == "delivered"]
    [["order_id", "customer_unique_id", "order_purchase_timestamp", "revenue"]]
    .dropna()
)

first_purchase = (
    cohort_base.groupby("customer_unique_id")["order_purchase_timestamp"]
    .min().reset_index()
    .rename(columns={"order_purchase_timestamp": "first_ts"})
)
first_purchase["cohort_month"] = (
    first_purchase["first_ts"].dt.to_period("M").dt.strftime("%Y-%m")
)

all_orders = cohort_base.merge(first_purchase, on="customer_unique_id")
all_orders["days_since_first"] = (
    all_orders["order_purchase_timestamp"] - all_orders["first_ts"]
).dt.days

repeat_orders = all_orders[all_orders["days_since_first"] > 0]

cohort_sizes = first_purchase.groupby("cohort_month")["customer_unique_id"].count()

coh_rows = []
for cohort_month, cohort_fp in first_purchase.groupby("cohort_month"):
    size = len(cohort_fp)
    cust = set(cohort_fp["customer_unique_id"])
    c_all = all_orders[all_orders["customer_unique_id"].isin(cust)]
    c_rep = repeat_orders[repeat_orders["customer_unique_id"].isin(cust)]

    row = {"cohort_month": cohort_month, "cohort_size": int(size)}
    for days in [30, 60, 90, 180]:
        rep_w = c_rep[c_rep["days_since_first"] <= days]
        row[f"ret_{days}d"] = rep_w["customer_unique_id"].nunique() / size
        all_w = c_all[c_all["days_since_first"] <= days]
        row[f"ltv_{days}d"] = all_w["revenue"].sum() / size
    coh_rows.append(row)

cohorts_real = pd.DataFrame(coh_rows).sort_values("cohort_month")

# Statistical outlier flag: 90d retention > 1.5 std below mean
mean_90 = cohorts_real["ret_90d"].mean()
std_90  = cohorts_real["ret_90d"].std()
cohorts_real["is_outlier"] = cohorts_real["ret_90d"] < (mean_90 - 1.5 * std_90)
cohorts_real.to_csv(OUT / "cohorts_real.csv", index=False)

overall_repeat = len(first_purchase[
    first_purchase["customer_unique_id"].isin(repeat_orders["customer_unique_id"])
]) / len(first_purchase)
print(f"  cohorts_real.csv                 ({len(cohorts_real)} cohorts)")
print(f"  Overall repeat purchase rate:    {overall_repeat:.1%}")

# ── 9. Seasonality (monthly demand, all delivered orders) ─────────────────────
print("Building seasonality data…")

season_monthly = (
    delivered.groupby("purchase_month")
    .agg(
        orders            = ("order_id",          "count"),
        revenue           = ("revenue",           "sum"),
        avg_review_score  = ("review_score",      "mean"),
        on_time_rate      = ("delivered_on_time", "mean"),
        avg_delivery_days = ("delivery_days",     "mean"),
    )
    .reset_index()
)
season_monthly["year"]      = season_monthly["purchase_month"].str[:4].astype(int)
season_monthly["month_num"] = season_monthly["purchase_month"].str[5:7].astype(int)

# Category mix by month — top 5 categories share over time
top5_cats = (
    delivered.groupby("primary_category")["order_id"].count()
    .nlargest(5).index.tolist()
)
cat_monthly = (
    delivered[delivered["primary_category"].isin(top5_cats)]
    .groupby(["purchase_month", "primary_category"])["order_id"]
    .count()
    .reset_index(name="orders")
)

season_monthly.to_csv(OUT / "seasonality_monthly.csv", index=False)
cat_monthly.to_csv(OUT / "seasonality_cat_monthly.csv", index=False)
print(f"  seasonality_monthly.csv          ({len(season_monthly)} rows)")
print(f"  seasonality_cat_monthly.csv      ({len(cat_monthly)} rows)")

# ── 10. Chargeback risk proxies ───────────────────────────────────────────────
print("Building chargeback risk data…")

delivered_pay = pay_master[pay_master["order_status"] == "delivered"].copy()

# Three independent evidence signals
delivered_pay["flag_1star"]        = (delivered_pay["review_score"] == 1).astype(int)
delivered_pay["flag_late"]         = (delivered_pay["days_late"] > 7).astype(int)
delivered_pay["flag_installments"] = (delivered_pay["max_installments"] >= 7).astype(int)
delivered_pay["risk_score"]        = (
    delivered_pay["flag_1star"] +
    delivered_pay["flag_late"] +
    delivered_pay["flag_installments"]
)
# Flagged = 2+ independent signals (high-confidence dispute proxy)
delivered_pay["is_flagged"] = delivered_pay["risk_score"] >= 2

flagged_only = delivered_pay[delivered_pay["is_flagged"]]

# Monthly: flagged orders and revenue at risk
cb_monthly_base = (
    delivered_pay.groupby("purchase_month")
    .agg(total_orders=("order_id", "count"), total_revenue=("revenue", "sum"),
         flagged_orders=("is_flagged", "sum"))
    .reset_index()
)
cb_flagged_rev = (
    flagged_only.groupby("purchase_month")["revenue"]
    .sum().reset_index(name="flagged_revenue")
)
cb_monthly = cb_monthly_base.merge(cb_flagged_rev, on="purchase_month", how="left")
cb_monthly["flagged_revenue"] = cb_monthly["flagged_revenue"].fillna(0)
cb_monthly["flag_rate"] = cb_monthly["flagged_orders"] / cb_monthly["total_orders"]
cb_monthly.to_csv(OUT / "chargeback_monthly.csv", index=False)

# By category: flag rate and revenue at risk
cb_cat_base = (
    delivered_pay.groupby("primary_category")
    .agg(total_orders=("order_id", "count"), flagged_orders=("is_flagged", "sum"),
         avg_risk_score=("risk_score", "mean"))
    .reset_index()
)
cb_cat_rev = (
    flagged_only.groupby("primary_category")["revenue"]
    .sum().reset_index(name="flagged_revenue")
)
cb_category = cb_cat_base.merge(cb_cat_rev, on="primary_category", how="left")
cb_category["flagged_revenue"] = cb_category["flagged_revenue"].fillna(0)
cb_category["flag_rate"] = cb_category["flagged_orders"] / cb_category["total_orders"]
cb_category = (
    cb_category[cb_category["total_orders"] >= 100]
    .sort_values("flag_rate", ascending=False)
)
cb_category.to_csv(OUT / "chargeback_by_category.csv", index=False)

# Evidence score distribution (0–3 signals)
cb_evidence = (
    delivered_pay.groupby("risk_score")
    .agg(orders=("order_id", "count"), revenue=("revenue", "sum"))
    .reset_index()
)
cb_evidence.to_csv(OUT / "chargeback_evidence.csv", index=False)

print(f"  chargeback_monthly.csv           ({len(cb_monthly)} rows)")
print(f"  chargeback_by_category.csv       ({len(cb_category)} rows)")
print(f"  chargeback_evidence.csv          ({len(cb_evidence)} rows)")

print("\nDone. All files written to data/")
