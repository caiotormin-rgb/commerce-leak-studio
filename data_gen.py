"""
Synthetic ecommerce data generator modeled on the Olist Brazilian
ecommerce dataset (structure, AOV, seasonality, categories).

Bakes in realistic attribution problems:
  - Meta overclaims by ~45% (view-through attribution window abuse)
  - Google overclaims by ~25% (PMax + cross-channel double-counting)
  - GA4 missing ~22% of Shopify orders (client-side tracking gaps)
  - One cohort (Mar 2017) with anomalously low retention
    (broad Meta targeting spike → lower-quality customer cohort)
"""

import numpy as np
import pandas as pd
from datetime import date, timedelta
import os

# ── Data path ─────────────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), 'files')

# ── Olist-calibrated constants ─────────────────────────────────────────────
START_DATE   = date(2016, 9, 1)   # Olist dataset start
N_WEEKS      = 104                # 2 years
BASE_WEEKLY_ORDERS = 420          # ~22k orders/year at start, growing
BASE_AOV_BRL = 137.0              # realistic Olist AOV

CATEGORIES = [
    ("bed_bath_table",      0.14),
    ("health_beauty",       0.12),
    ("sports_leisure",      0.10),
    ("computers_accessories",0.09),
    ("furniture_decor",     0.08),
    ("housewares",          0.07),
    ("watches_gifts",       0.06),
    ("telephony",           0.05),
    ("auto",                0.05),
    ("toys",                0.05),
    ("garden_tools",        0.04),
    ("cool_stuff",          0.04),
    ("other",               0.11),
]

BRAZIL_STATES = [
    ("SP", "Southeast", -23.55, -46.63, 0.38),
    ("RJ", "Southeast", -22.91, -43.17, 0.12),
    ("MG", "Southeast", -19.92, -43.94, 0.11),
    ("RS", "South", -30.03, -51.23, 0.07),
    ("PR", "South", -25.43, -49.27, 0.06),
    ("SC", "South", -27.60, -48.55, 0.04),
    ("BA", "Northeast", -12.97, -38.50, 0.04),
    ("DF", "Central-West", -15.79, -47.88, 0.03),
    ("GO", "Central-West", -16.68, -49.25, 0.03),
    ("PE", "Northeast", -8.05, -34.88, 0.03),
    ("CE", "Northeast", -3.73, -38.52, 0.025),
    ("PA", "North", -1.45, -48.49, 0.02),
    ("ES", "Southeast", -20.32, -40.34, 0.015),
    ("MT", "Central-West", -15.60, -56.10, 0.01),
    ("AM", "North", -3.12, -60.02, 0.01),
]

RETURN_REASONS = [
    ("Late delivery", 0.30),
    ("Damaged item", 0.22),
    ("Wrong item", 0.16),
    ("Changed mind", 0.14),
    ("Quality issue", 0.12),
    ("Fraud/cancelled", 0.06),
]

# Seasonality multipliers by month (BR calendar)
SEASONALITY = {
    1: 0.85,   # post-holiday dip
    2: 0.80,   # Carnaval
    3: 0.88,
    4: 0.92,
    5: 1.35,   # Dia das Mães ★
    6: 0.95,
    7: 0.98,
    8: 1.10,   # Dia dos Pais
    9: 1.05,
    10: 1.08,
    11: 1.75,  # Black Friday BR ★★
    12: 1.45,  # Natal ★
}


def _seasonality(dt: date) -> float:
    return SEASONALITY[dt.month]


def load_orders() -> pd.DataFrame:
    """Load and preprocess orders data."""
    orders = pd.read_csv(os.path.join(DATA_DIR, 'olist_orders_dataset.csv'))
    orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])
    orders = orders[orders['order_status'] == 'delivered']  # Only delivered orders
    return orders


def load_order_items() -> pd.DataFrame:
    """Load order items data."""
    items = pd.read_csv(os.path.join(DATA_DIR, 'olist_order_items_dataset.csv'))
    return items


def load_products() -> pd.DataFrame:
    """Load products data with English category names."""
    products = pd.read_csv(os.path.join(DATA_DIR, 'olist_products_dataset.csv'))
    translation = pd.read_csv(os.path.join(DATA_DIR, 'product_category_name_translation.csv'))
    products = products.merge(translation, on='product_category_name', how='left')
    products['product_category_name_english'] = products['product_category_name_english'].fillna(products['product_category_name'])
    return products


def load_customers() -> pd.DataFrame:
    """Load customers data."""
    customers = pd.read_csv(os.path.join(DATA_DIR, 'olist_customers_dataset.csv'))
    return customers


def generate_weekly_real() -> pd.DataFrame:
    """Generate weekly data from real Olist dataset."""
    orders = load_orders()
    items = load_order_items()
    
    # Merge orders and items
    order_revenue = items.groupby('order_id')['price'].sum().reset_index()
    orders = orders.merge(order_revenue, on='order_id', how='left')
    orders['price'] = orders['price'].fillna(0)
    
    # Group by week
    orders['week_start'] = orders['order_purchase_timestamp'].dt.to_period('W').dt.start_time
    weekly = orders.groupby('week_start').agg({
        'order_id': 'count',
        'price': 'sum'
    }).rename(columns={'order_id': 'shopify_orders', 'price': 'shopify_revenue'}).reset_index()
    
    # Sort by week
    weekly = weekly.sort_values('week_start')
    
    # Add synthetic attribution (since real data doesn't have it)
    rng = np.random.default_rng(42)
    rows = []
    for _, wk in weekly.iterrows():
        week_start = wk['week_start']
        shopify_orders = wk['shopify_orders']
        shopify_revenue = wk['shopify_revenue']
        
        # Ad spend
        google_spend = shopify_revenue * rng.uniform(0.10, 0.14)
        meta_spend = shopify_revenue * rng.uniform(0.13, 0.18) * (
            1.3 if week_start.month in (5, 11) else 1.0
        )
        email_cost = shopify_revenue * rng.uniform(0.01, 0.02)
        total_spend = google_spend + meta_spend + email_cost
        
        # True attribution
        google_true = shopify_revenue * rng.uniform(0.28, 0.36)
        meta_true = shopify_revenue * rng.uniform(0.22, 0.32)
        email_true = shopify_revenue * rng.uniform(0.08, 0.14)
        organic_true = shopify_revenue - google_true - meta_true - email_true
        
        # Reported
        meta_reported_revenue = shopify_revenue * rng.uniform(0.55, 0.70)
        google_reported_revenue = shopify_revenue * rng.uniform(0.45, 0.60)
        email_reported_revenue = shopify_revenue * rng.uniform(0.20, 0.30)

        # GA4 (missing ~22% of Shopify conversions)
        ga4_missing_rate = rng.uniform(0.18, 0.28)
        ga4_revenue = shopify_revenue * (1 - ga4_missing_rate)
        ga4_sessions = int(shopify_orders / rng.uniform(0.024, 0.032))

        mer = shopify_revenue / total_spend if total_spend > 0 else 0
        google_reported_roas = google_reported_revenue / google_spend
        meta_reported_roas = meta_reported_revenue / meta_spend
        google_true_roas = google_true / google_spend
        meta_true_roas = meta_true / meta_spend
        total_claimed = google_reported_revenue + meta_reported_revenue + email_reported_revenue
        overclaim_pct = (total_claimed / shopify_revenue - 1) * 100 if shopify_revenue > 0 else 0
        
        rows.append({
            'week_start': week_start,
            'week_num': (week_start - pd.Timestamp(START_DATE)).days // 7 + 1,
            'year': week_start.year,
            'month': week_start.month,
            'shopify_orders': shopify_orders,
            'shopify_revenue': round(shopify_revenue, 2),
            'shopify_aov': round(shopify_revenue / shopify_orders, 2) if shopify_orders > 0 else 0,
            'google_spend': round(google_spend, 2),
            'meta_spend': round(meta_spend, 2),
            'email_cost': round(email_cost, 2),
            'total_spend': round(total_spend, 2),
            'google_true': round(google_true, 2),
            'meta_true': round(meta_true, 2),
            'email_true': round(email_true, 2),
            'organic_true': round(organic_true, 2),
            'google_reported_revenue': round(google_reported_revenue, 2),
            'meta_reported_revenue': round(meta_reported_revenue, 2),
            'email_reported_revenue': round(email_reported_revenue, 2),
            'total_claimed': round(total_claimed, 2),
            'overclaim_pct': round(overclaim_pct, 1),
            'google_reported_roas': round(google_reported_roas, 2),
            'meta_reported_roas': round(meta_reported_roas, 2),
            'google_true_roas': round(google_true_roas, 2),
            'meta_true_roas': round(meta_true_roas, 2),
            'ga4_revenue': round(ga4_revenue, 2),
            'ga4_sessions': ga4_sessions,
            'ga4_missing_pct': round(ga4_missing_rate * 100, 1),
            'mer': round(mer, 3),
            'season_label': _season_label(week_start.date()),
        })
    
    return pd.DataFrame(rows)

def generate_cohorts_real() -> pd.DataFrame:
    """Generate monthly cohorts from real data."""
    orders = load_orders()
    customers = load_customers()
    items = load_order_items()
    
    # Merge to get customer unique id and order dates
    orders = orders.merge(customers[['customer_id', 'customer_unique_id']], on='customer_id')
    
    # Get first order date per customer
    first_orders = orders.groupby('customer_unique_id')['order_purchase_timestamp'].min().reset_index()
    first_orders['cohort_month'] = first_orders['order_purchase_timestamp'].dt.to_period('M').dt.start_time
    first_orders['cohort_month_str'] = first_orders['cohort_month'].dt.strftime('%Y-%m')
    
    # Count new customers per cohort
    cohort_sizes = first_orders.groupby('cohort_month_str').size().reset_index(name='new_customers')
    cohort_sizes['cohort_date'] = pd.to_datetime(cohort_sizes['cohort_month_str'])
    
    # Calculate retention
    # For each cohort, see orders in subsequent months
    rows = []
    for _, cohort in cohort_sizes.iterrows():
        cohort_month = cohort['cohort_month_str']
        cohort_date = cohort['cohort_date']
        new_customers = cohort['new_customers']
        
        # Get customers in this cohort
        cohort_customers = first_orders[first_orders['cohort_month_str'] == cohort_month]['customer_unique_id']
        
        # Get all orders by these customers
        cohort_orders = orders[orders['customer_unique_id'].isin(cohort_customers)]
        
        # Calculate retention at different periods
        base_date = cohort_date
        periods = [30, 60, 90, 180]
        retentions = {}
        ltvs = {}
        
        # First order value average
        first_order_revenue = items[items['order_id'].isin(cohort_orders[cohort_orders['order_purchase_timestamp'].dt.to_period('M') == cohort_date.to_period('M')]['order_id'])]['price'].mean()
        avg_first_order = first_order_revenue if not pd.isna(first_order_revenue) else BASE_AOV_BRL
        
        for days in periods:
            end_date = base_date + pd.Timedelta(days=days)
            period_orders = cohort_orders[cohort_orders['order_purchase_timestamp'] <= end_date]
            repeat_customers = period_orders['customer_unique_id'].nunique()
            ret = repeat_customers / new_customers if new_customers > 0 else 0
            retentions[f'ret_{days}d'] = ret
            
            # LTV approximation
            period_revenue = items[items['order_id'].isin(period_orders['order_id'])]['price'].sum()
            ltv = period_revenue / new_customers if new_customers > 0 else 0
            ltvs[f'ltv_{days}d'] = ltv
        
        # For anomaly, check if March 2017
        is_anomaly = (cohort_date.year == 2017 and cohort_date.month == 3)
        
        rows.append({
            'cohort_month': cohort_month,
            'cohort_date': cohort_date,
            'new_customers': new_customers,
            'is_anomaly': is_anomaly,
            'meta_pct': 0.4,  # Placeholder, since no real attribution
            'google_pct': 0.3,
            'organic_pct': 0.3,
            'ret_30d': retentions['ret_30d'],
            'ret_60d': retentions['ret_60d'],
            'ret_90d': retentions['ret_90d'],
            'ret_180d': retentions['ret_180d'],
            'avg_first_order': avg_first_order,
            'ltv_30d': ltvs['ltv_30d'],
            'ltv_90d': ltvs['ltv_90d'],
            'ltv_180d': ltvs['ltv_180d'],
        })
    
    df = pd.DataFrame(rows)
    df = df.sort_values('cohort_date')
    return df

def generate_weekly(seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []

    for w in range(N_WEEKS):
        week_start = START_DATE + timedelta(weeks=w)
        week_num   = w + 1
        season     = _seasonality(week_start)
        growth     = 1 + (w / N_WEEKS) * 0.9         # ~90% total growth over 2yr
        noise      = rng.normal(1.0, 0.05)

        # ── Shopify ground truth ───────────────────────────────────────────
        orders   = int(BASE_WEEKLY_ORDERS * season * growth * noise)
        aov      = BASE_AOV_BRL * rng.normal(1.0, 0.08)
        shopify_revenue = orders * aov

        # ── Ad spend ──────────────────────────────────────────────────────
        # Google Shopping + Search: grows with revenue, efficiency improving
        google_spend = shopify_revenue * rng.uniform(0.10, 0.14)
        # Meta: higher share, peaks on BR holidays
        meta_spend   = shopify_revenue * rng.uniform(0.13, 0.18) * (
            1.3 if week_start.month in (5, 11) else 1.0
        )
        email_cost   = shopify_revenue * rng.uniform(0.01, 0.02)
        total_spend  = google_spend + meta_spend + email_cost

        # ── True attribution (ground truth we reveal) ─────────────────────
        # Splits that actually add up to shopify_revenue
        google_true  = shopify_revenue * rng.uniform(0.28, 0.36)
        meta_true    = shopify_revenue * rng.uniform(0.22, 0.32)
        email_true   = shopify_revenue * rng.uniform(0.08, 0.14)
        organic_true = shopify_revenue - google_true - meta_true - email_true

        # ── Platform-reported (inflated) ─────────────────────────────────
        # Reality: each platform claims credit for ALL orders where their
        # ad was in the attribution window — so they double/triple count.
        # Meta: claims 55-70% of ALL Shopify revenue (7d click / 1d view window)
        meta_reported_revenue = shopify_revenue * rng.uniform(0.55, 0.70)
        # Google: claims 45-60% of ALL Shopify revenue (data-driven + DDA)
        google_reported_revenue = shopify_revenue * rng.uniform(0.45, 0.60)
        # Email: claims 20-30% of ALL Shopify revenue
        email_reported_revenue = shopify_revenue * rng.uniform(0.20, 0.30)

        # ── GA4 (missing ~22% of Shopify conversions) ─────────────────────
        ga4_missing_rate = rng.uniform(0.18, 0.28)   # ad blockers + ITP
        ga4_revenue      = shopify_revenue * (1 - ga4_missing_rate)
        ga4_sessions     = int(orders / rng.uniform(0.024, 0.032))  # ~3% CVR

        # ── Derived metrics ───────────────────────────────────────────────
        mer = shopify_revenue / total_spend if total_spend > 0 else 0
        google_reported_roas = google_reported_revenue / google_spend
        meta_reported_roas   = meta_reported_revenue / meta_spend
        google_true_roas     = google_true / google_spend
        meta_true_roas       = meta_true / meta_spend

        # Total claimed by platforms (the "impossible math")
        total_claimed = (
            google_reported_revenue + meta_reported_revenue + email_reported_revenue
        )
        overclaim_pct = (total_claimed / shopify_revenue - 1) * 100

        rows.append({
            "week_start":              week_start,
            "week_num":                week_num,
            "year":                    week_start.year,
            "month":                   week_start.month,
            "season_label":            _season_label(week_start),

            # Shopify (truth)
            "shopify_orders":          orders,
            "shopify_revenue":         round(shopify_revenue, 2),
            "shopify_aov":             round(aov, 2),

            # Spend
            "google_spend":            round(google_spend, 2),
            "meta_spend":              round(meta_spend, 2),
            "email_cost":              round(email_cost, 2),
            "total_spend":             round(total_spend, 2),

            # Platform-reported (inflated)
            "google_reported_revenue": round(google_reported_revenue, 2),
            "meta_reported_revenue":   round(meta_reported_revenue, 2),
            "email_reported_revenue":  round(email_reported_revenue, 2),
            "total_claimed":           round(total_claimed, 2),
            "overclaim_pct":           round(overclaim_pct, 1),

            "google_reported_roas":    round(google_reported_roas, 2),
            "meta_reported_roas":      round(meta_reported_roas, 2),

            # True attribution
            "google_true":             round(google_true, 2),
            "meta_true":               round(meta_true, 2),
            "email_true":              round(email_true, 2),
            "organic_true":            round(organic_true, 2),
            "google_true_roas":        round(google_true_roas, 2),
            "meta_true_roas":          round(meta_true_roas, 2),

            # GA4 (broken)
            "ga4_revenue":             round(ga4_revenue, 2),
            "ga4_sessions":            ga4_sessions,
            "ga4_missing_pct":         round(ga4_missing_rate * 100, 1),

            # MER
            "mer":                     round(mer, 3),
        })

    df = pd.DataFrame(rows)
    df["week_start"] = pd.to_datetime(df["week_start"])
    return df


def generate_cohorts(seed: int = 42) -> pd.DataFrame:
    """
    Monthly cohort retention + LTV table.
    Bakes in a March 2017 anomaly (low retention from Meta broad targeting spike).
    """
    rng = np.random.default_rng(seed + 1)
    rows = []

    for m in range(24):  # 24 months
        cohort_date = date(2016, 9, 1) + pd.DateOffset(months=m)
        cohort_month = cohort_date.strftime("%Y-%m")
        season = SEASONALITY[cohort_date.month]
        
        new_customers = int(rng.normal(1400, 200) * season * (1 + m * 0.03))

        # March 2017 anomaly: Meta broad targeting spike brought low-quality cohort
        is_anomaly = (cohort_date.year == 2017 and cohort_date.month == 3)

        if is_anomaly:
            base_retention = rng.uniform(0.10, 0.15)   # very low: 10–15%
            meta_pct = 0.62                              # Meta dominated acquisition
        else:
            base_retention = rng.uniform(0.22, 0.32)
            meta_pct = rng.uniform(0.28, 0.42)

        # Retention curves (monotone decreasing)
        ret_30d  = base_retention
        ret_60d  = ret_30d  * rng.uniform(0.55, 0.72)
        ret_90d  = ret_60d  * rng.uniform(0.60, 0.75)
        ret_180d = ret_90d  * rng.uniform(0.55, 0.70)

        avg_first_order = BASE_AOV_BRL * rng.normal(1.0, 0.12)

        ltv_30d  = avg_first_order * (1 + ret_30d  * rng.uniform(0.8, 1.2))
        ltv_90d  = ltv_30d         * (1 + ret_90d  * rng.uniform(0.9, 1.3))
        ltv_180d = ltv_90d         * (1 + ret_180d * rng.uniform(0.8, 1.1))

        rows.append({
            "cohort_month":    cohort_month,
            "cohort_date":     cohort_date,
            "new_customers":   new_customers,
            "is_anomaly":      is_anomaly,
            "meta_pct":        round(meta_pct, 2),
            "google_pct":      round(rng.uniform(0.20, 0.35), 2),
            "organic_pct":     round(1 - meta_pct - 0.28, 2),
            "ret_30d":         round(ret_30d, 3),
            "ret_60d":         round(ret_60d, 3),
            "ret_90d":         round(ret_90d, 3),
            "ret_180d":        round(ret_180d, 3),
            "avg_first_order": round(avg_first_order, 2),
            "ltv_30d":         round(ltv_30d, 2),
            "ltv_90d":         round(ltv_90d, 2),
            "ltv_180d":        round(ltv_180d, 2),
        })

    df = pd.DataFrame(rows)
    df["cohort_date"] = pd.to_datetime(df["cohort_date"])
    return df


def generate_categories_real() -> pd.DataFrame:
    """Generate category-level revenue from real data."""
    orders = load_orders()
    items = load_order_items()
    products = load_products()
    
    # Merge items with products
    items = items.merge(products[['product_id', 'product_category_name_english']], on='product_id', how='left')
    items['category'] = items['product_category_name_english'].fillna('other')
    
    # Merge with orders for dates
    items = items.merge(orders[['order_id', 'order_purchase_timestamp']], on='order_id')
    
    # Group by week and category
    items['week_start'] = items['order_purchase_timestamp'].dt.to_period('W').dt.start_time
    categories = items.groupby(['week_start', 'category']).agg({
        'price': 'sum',
        'order_id': 'count'
    }).reset_index().rename(columns={'price': 'revenue', 'order_id': 'orders'})
    
    # Map to the expected categories, group others
    expected_cats = [cat for cat, _ in CATEGORIES]
    categories['category'] = categories['category'].apply(lambda x: x if x in expected_cats else 'other')
    categories = categories.groupby(['week_start', 'category']).sum().reset_index()
    
    return categories


def generate_categories(weekly_df: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    """Category-level revenue breakdown for product mix view."""
    rng = np.random.default_rng(seed + 2)
    rows = []
    for _, wk in weekly_df.iterrows():
        remaining = wk["shopify_revenue"]
        for cat, share in CATEGORIES[:-1]:
            noise = rng.normal(share, share * 0.15)
            noise = max(0.01, noise)
            rev = wk["shopify_revenue"] * noise
            remaining -= rev
            rows.append({
                "week_start": wk["week_start"],
                "category":   cat,
                "revenue":    round(max(rev, 0), 2),
                "orders":     int(wk["shopify_orders"] * noise),
            })
        rows.append({
            "week_start": wk["week_start"],
            "category":   "other",
            "revenue":    round(max(remaining, 0), 2),
            "orders":     int(max(wk["shopify_orders"] * 0.11, 0)),
        })

    return pd.DataFrame(rows)


def generate_reviews(weekly_df: pd.DataFrame, categories_df: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    """Weekly review quality signals by product category."""
    rng = np.random.default_rng(seed + 3)
    category_penalties = {
        "furniture_decor": -0.22,
        "computers_accessories": -0.16,
        "auto": -0.12,
        "toys": -0.08,
        "health_beauty": 0.12,
        "watches_gifts": 0.08,
        "bed_bath_table": 0.05,
    }
    weekly_lookup = weekly_df.set_index("week_start")
    rows = []

    for _, cat in categories_df.iterrows():
        week = cat["week_start"]
        wk = weekly_lookup.loc[week]
        month = int(wk["month"])
        category = cat["category"]
        review_count = max(1, int(cat["orders"] * rng.uniform(0.42, 0.62)))

        season_penalty = -0.20 if month in (11, 12) else (-0.08 if month in (5, 8) else 0)
        score = 4.28 + category_penalties.get(category, 0) + season_penalty + rng.normal(0, 0.12)
        score = float(np.clip(score, 2.8, 4.9))
        one_two_star_share = float(np.clip(0.28 - (score - 3.0) * 0.12 + rng.normal(0, 0.015), 0.03, 0.35))
        comment_share = float(np.clip(0.34 + one_two_star_share * 0.6 + rng.normal(0, 0.03), 0.18, 0.62))
        response_hours = float(np.clip(16 + one_two_star_share * 90 + rng.normal(0, 8), 6, 72))

        rows.append({
            "week_start": week,
            "category": category,
            "review_count": review_count,
            "avg_review_score": round(score, 2),
            "one_two_star_share": round(one_two_star_share, 3),
            "comment_share": round(comment_share, 3),
            "avg_response_hours": round(response_hours, 1),
        })

    return pd.DataFrame(rows)


def generate_geo(weekly_df: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    """Weekly state-level demand, service, and quality signals."""
    rng = np.random.default_rng(seed + 4)
    rows = []

    for _, wk in weekly_df.iterrows():
        for state, region, lat, lon, base_share in BRAZIL_STATES:
            regional_noise = rng.normal(1.0, 0.08)
            share = max(base_share * regional_noise, 0.002)
            orders = max(1, int(wk["shopify_orders"] * share))
            revenue = wk["shopify_revenue"] * share * rng.normal(1.0, 0.06)
            distance_penalty = {"Southeast": 0.0, "South": 0.7, "Central-West": 1.4, "Northeast": 2.2, "North": 3.2}[region]
            delivery_days = np.clip(rng.normal(6.0 + distance_penalty, 1.0), 3.2, 13.5)
            late_delivery_rate = np.clip(0.06 + distance_penalty * 0.025 + rng.normal(0, 0.012), 0.02, 0.24)
            review_score = np.clip(4.35 - late_delivery_rate * 3.2 + rng.normal(0, 0.08), 3.1, 4.8)
            return_rate = np.clip(0.035 + late_delivery_rate * 0.32 + rng.normal(0, 0.006), 0.02, 0.13)

            rows.append({
                "week_start": wk["week_start"],
                "state": state,
                "region": region,
                "lat": lat,
                "lon": lon,
                "orders": orders,
                "revenue": round(revenue, 2),
                "delivery_days": round(delivery_days, 1),
                "late_delivery_rate": round(late_delivery_rate, 3),
                "review_score": round(review_score, 2),
                "return_rate": round(return_rate, 3),
            })

    return pd.DataFrame(rows)


def generate_returns(weekly_df: pd.DataFrame, categories_df: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    """Weekly return/refund patterns by category and reason."""
    rng = np.random.default_rng(seed + 5)
    category_risk = {
        "computers_accessories": 0.022,
        "furniture_decor": 0.020,
        "auto": 0.018,
        "toys": 0.015,
        "watches_gifts": 0.014,
        "health_beauty": -0.004,
        "bed_bath_table": -0.003,
    }
    weekly_lookup = weekly_df.set_index("week_start")
    rows = []

    for _, cat in categories_df.iterrows():
        wk = weekly_lookup.loc[cat["week_start"]]
        category = cat["category"]
        seasonal_risk = 0.016 if int(wk["month"]) in (11, 12) else (0.008 if int(wk["month"]) in (5, 8) else 0)
        base_rate = 0.055 + category_risk.get(category, 0) + seasonal_risk + rng.normal(0, 0.006)
        return_rate = float(np.clip(base_rate, 0.018, 0.14))
        returns_count = max(0, int(cat["orders"] * return_rate))
        refund_value = cat["revenue"] * return_rate * rng.uniform(0.82, 1.05)

        reason_mix = np.array([weight for _, weight in RETURN_REASONS], dtype=float)
        if category in {"furniture_decor", "auto"}:
            reason_mix[1] += 0.08
        if int(wk["month"]) in (11, 12):
            reason_mix[0] += 0.10
        reason_mix = reason_mix / reason_mix.sum()

        for (reason, _), reason_share in zip(RETURN_REASONS, reason_mix):
            reason_returns = int(round(returns_count * reason_share))
            rows.append({
                "week_start": cat["week_start"],
                "category": category,
                "reason": reason,
                "returns": reason_returns,
                "refund_value": round(refund_value * reason_share, 2),
                "return_rate": round(return_rate, 3),
            })

    return pd.DataFrame(rows)


def _season_label(dt: date) -> str:
    if dt.month == 11:
        return "Black Friday"
    elif dt.month == 5:
        return "Dia das Mães"
    elif dt.month == 12:
        return "Natal"
    elif dt.month == 8:
        return "Dia dos Pais"
    elif dt.month == 2:
        return "Carnaval"
    return ""


def load_all(
    seed: int = 42,
    use_real: bool | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Return the dashboard-ready dataset.

    The Streamlit app expects attribution fields that only exist in the
    synthetic model. Loading the raw Olist CSVs is much slower and returns a
    narrower schema, so keep it opt-in for exploration.
    """
    if use_real is None:
        use_real = os.getenv("USE_REAL_OLIST", "").lower() in {"1", "true", "yes"}

    if not use_real:
        weekly = generate_weekly(seed=seed)
        cohorts = generate_cohorts(seed=seed)
        categories = generate_categories(weekly, seed=seed)
        reviews = generate_reviews(weekly, categories, seed=seed)
        geo = generate_geo(weekly, seed=seed)
        returns = generate_returns(weekly, categories, seed=seed)
        return weekly, cohorts, categories, reviews, geo, returns

    weekly     = generate_weekly_real()
    cohorts    = generate_cohorts_real()
    categories = generate_categories_real()
    reviews    = generate_reviews(weekly, categories, seed=seed)
    geo        = generate_geo(weekly, seed=seed)
    returns    = generate_returns(weekly, categories, seed=seed)
    return weekly, cohorts, categories, reviews, geo, returns
