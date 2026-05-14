"""
Orders & Delivery — Insights tab 2
Did orders ship well? Are customers coming back?
"""
import numpy as np
import streamlit as st
import plotly.graph_objects as go

from shared import plot_layout, COLORS


def render(cohorts_real, rv_distribution, rv_monthly, rv_by_category,
           fl_review_lateness, fl_by_category, fl_monthly, geo_real):

    # ── Compute headline numbers ──────────────────────────────────────────
    has_cohorts = cohorts_real is not None
    has_fl      = fl_review_lateness is not None and fl_monthly is not None

    if has_cohorts:
        sz            = cohorts_real["cohort_size"]
        repeat_rate   = (cohorts_real["ret_180d"] * sz).sum() / sz.sum()
        avg_ltv       = cohorts_real["ltv_180d"].mean()
        total_buyers  = int(sz.sum())
    if has_fl:
        w_wt          = fl_monthly["orders"]
        on_time       = np.average(fl_monthly["on_time_rate"],      weights=w_wt)
        avg_days      = np.average(fl_monthly["avg_delivery_days"], weights=w_wt)
        avg_review_fl = np.average(fl_monthly["avg_review_score"],  weights=w_wt)

    # ── Takeaway ─────────────────────────────────────────────────────────
    repeat_str = f"{repeat_rate*100:.1f}%" if has_cohorts else "data pending"
    ontime_str = f"{on_time*100:.1f}%"     if has_fl      else "data pending"
    st.markdown(f"""
<div class="callout callout-amber" style="font-size:14px;line-height:1.9">
<strong>The short version:</strong>&nbsp; Only <strong>{repeat_str}</strong> of customers
placed a second order within 180 days. Orders delivered on time average <strong>4.4★</strong>;
orders arriving 8–14 days late drop to <strong>~2.0★</strong>.
Fixing delivery speed is the fastest lever to improve reviews and repeat purchases.
</div>
""", unsafe_allow_html=True)

    # ── KPIs ──────────────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)

    if has_cohorts:
        k1.metric(
            "Customers acquired", f"{total_buyers:,}",
            help="Unique first-time buyers in the Olist dataset (Sep 2016 – Oct 2018).",
        )
        k2.metric(
            "Came back within 180 days", f"{repeat_rate*100:.1f}%",
            delta_color="inverse",
            help="Share of first-time buyers who placed at least one more order within 180 days. "
                 "Analysts call this the 180-day repeat rate or retention rate.",
        )
        k3.metric(
            "Avg 6-month value per buyer", f"R${avg_ltv:.0f}",
            help="Average total revenue per acquired customer over their first 180 days. "
                 "Also called LTV (lifetime value) in the 180-day window.",
        )
    else:
        k1.metric("Customers acquired", "—", "build Olist files")
        k2.metric("Came back within 180 days", "—")
        k3.metric("Avg 6-month value per buyer", "—")

    if has_fl:
        k4.metric(
            "Orders delivered on time", f"{on_time*100:.1f}%",
            help="Share of orders delivered on or before the estimated delivery date, across all categories and states.",
        )
    else:
        k4.metric("Orders delivered on time", "—")

    st.divider()

    # ── Q1: Are customers coming back? ────────────────────────────────────
    st.markdown("### Are customers coming back after their first order?")

    if not has_cohorts:
        st.warning("Run `python scripts/build_olist_data.py` to load cohort data.", icon="⚙️")
    else:
        st.markdown("""
<div class="callout callout-amber">
<strong>The retention problem:</strong> Only <strong>2.1% of customers</strong> placed a second
order within 180 days. Acquisition is not compounding into repeat revenue —
customer lifetime value grows almost entirely from the first order, not from loyalty.
</div>
""", unsafe_allow_html=True)

        col_c1, col_c2 = st.columns([3, 2])

        with col_c1:
            hm = (
                cohorts_real[["cohort_month", "ret_30d", "ret_60d", "ret_90d", "ret_180d"]]
                .set_index("cohort_month") * 100
            )
            hm.columns = ["30 days", "60 days", "90 days", "180 days"]

            fig_hm = go.Figure(go.Heatmap(
                z=hm.values,
                x=hm.columns.tolist(),
                y=hm.index.tolist(),
                colorscale=[
                    [0.0, "#09090e"],
                    [0.3, "#2a1800"],
                    [0.6, "#7a5200"],
                    [1.0, "#f5c542"],
                ],
                zmin=0, zmax=8,
                text=hm.round(1).astype(str) + "%",
                texttemplate="%{text}",
                textfont=dict(size=9),
                hovertemplate="Cohort: %{y}<br>Within: %{x}<br>Returned: %{z:.1f}%<extra></extra>",
            ))
            for i, row in enumerate(cohorts_real.itertuples()):
                if row.is_outlier:
                    fig_hm.add_shape(
                        type="rect", x0=-0.5, x1=3.5, y0=i - 0.5, y1=i + 0.5,
                        line=dict(color="#ff5566", width=2),
                    )
                    fig_hm.add_annotation(
                        x=3.6, y=i, text="⚠", showarrow=False,
                        font=dict(color="#ff5566", size=11), xanchor="left",
                    )
            fig_hm.update_layout(**plot_layout(
                title="% of buyers who made a second purchase  — by acquisition month",
                height=480,
                xaxis=dict(side="top"),
            ))
            st.plotly_chart(fig_hm, use_container_width=True)
            st.caption("Red borders = cohorts with unusually low retention vs peers. "
                       "These months often coincide with a delivery or quality problem worth investigating.")

        with col_c2:
            fig_ltv = go.Figure()
            for _, row in cohorts_real.iterrows():
                color   = "#ff5566" if row["is_outlier"] else COLORS["retention"]
                opacity = 1.0       if row["is_outlier"] else 0.22
                width   = 2.0       if row["is_outlier"] else 0.8
                fig_ltv.add_trace(go.Scatter(
                    x=[30, 60, 90, 180],
                    y=[row["ltv_30d"], row["ltv_60d"], row["ltv_90d"], row["ltv_180d"]],
                    mode="lines",
                    name=row["cohort_month"],
                    line=dict(color=color, width=width),
                    opacity=opacity,
                    showlegend=False,
                ))
            med = cohorts_real[["ltv_30d", "ltv_60d", "ltv_90d", "ltv_180d"]].median()
            fig_ltv.add_trace(go.Scatter(
                x=[30, 60, 90, 180],
                y=[med["ltv_30d"], med["ltv_60d"], med["ltv_90d"], med["ltv_180d"]],
                name="Median",
                mode="lines+markers",
                line=dict(color=COLORS["retention"], width=2.5, dash="dash"),
                marker=dict(size=6),
            ))
            fig_ltv.update_layout(**plot_layout(
                title="Revenue per buyer over their first 180 days",
                height=280,
                xaxis=dict(title="Days since first purchase", tickvals=[30, 60, 90, 180]),
                yaxis=dict(title="Revenue (BRL)"),
                legend=dict(orientation="h", y=1.15),
            ))
            st.plotly_chart(fig_ltv, use_container_width=True)
            st.caption("Red lines = low-retention cohorts. Flat curves = almost all value comes from the first order.")

        st.markdown(f"""
<div class="callout">
<strong>What this means for spend:</strong> With a 180-day repeat rate below 3%,
every R$1 of ad spend has to earn its margin from the first order alone.
Moving repeat rate from {repeat_rate*100:.1f}% to 5% would add roughly
<strong>R${(0.05 - repeat_rate) * total_buyers * avg_ltv:,.0f}</strong> in incremental revenue
from the existing customer base — no new acquisition required.
</div>
""", unsafe_allow_html=True)

    st.divider()

    # ── Q2: Is delivery hurting reviews and repeat purchases? ─────────────
    st.markdown("### Is slow delivery driving customers away?")
    st.markdown(
        '<p style="color:#8d8daf;font-size:14px;margin:-8px 0 16px">'
        "Late deliveries don't just frustrate — they leave 1-star reviews that suppress future sales."
        "</p>",
        unsafe_allow_html=True,
    )

    if not has_fl:
        st.warning("Run `python scripts/build_olist_data.py` to load fulfillment data.", icon="⚙️")
    else:
        col_f1, col_f2 = st.columns([3, 2])

        with col_f1:
            BUCKET_COLORS = ["#22d3a0", "#f5c542", "#ff8a4c", "#ff6b6b", "#ff2244"]
            fig_late = go.Figure(go.Bar(
                x=fl_review_lateness["bucket"],
                y=fl_review_lateness["avg_score"],
                marker_color=BUCKET_COLORS,
                text=fl_review_lateness["avg_score"].map(lambda v: f"{v:.2f}★"),
                textposition="outside",
                customdata=fl_review_lateness["order_count"],
                hovertemplate=(
                    "<b>%{x}</b><br>Avg review: %{y:.2f}★<br>"
                    "Orders: %{customdata:,}<extra></extra>"
                ),
            ))
            fig_late.update_layout(**plot_layout(
                title="How late delivery destroys review scores",
                height=340,
                yaxis=dict(title="Avg review score", range=[1, 5.5]),
                xaxis=dict(title=""),
            ))
            st.plotly_chart(fig_late, use_container_width=True)
            st.markdown("""
<div class="callout callout-red">
<strong>The link:</strong> On-time orders average <strong>4.4★</strong>.
Orders arriving 8–14 days late drop to <strong>~2.0★</strong>.
Bad reviews cut repeat purchase. Fulfillment SLA is a direct retention lever, not just an ops metric.
</div>
""", unsafe_allow_html=True)

        with col_f2:
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(
                x=fl_monthly["purchase_month"],
                y=fl_monthly["on_time_rate"] * 100,
                name="On-time %",
                mode="lines+markers",
                line=dict(color=COLORS["fulfillment"], width=2),
                marker=dict(size=4),
            ))
            fig_trend.add_trace(go.Scatter(
                x=fl_monthly["purchase_month"],
                y=fl_monthly["avg_delivery_days"],
                name="Avg days",
                mode="lines",
                line=dict(color=COLORS["geo"], width=2, dash="dot"),
                yaxis="y2",
            ))
            fig_trend.update_layout(**plot_layout(
                title="On-time rate & delivery speed over time",
                height=320,
                xaxis=dict(title="", tickangle=-45, nticks=8),
                yaxis=dict(title="On-time %", range=[70, 100]),
                yaxis2=dict(
                    title="Avg days", overlaying="y", side="right",
                    showgrid=False, range=[0, 40],
                ),
                legend=dict(orientation="h", y=1.18),
            ))
            st.plotly_chart(fig_trend, use_container_width=True)
            st.markdown("""
<div class="callout callout-green">
Avg delivery improved from ~15 days in late 2016 to ~9 days by mid-2018 as the seller network
matured — and review scores improved in lockstep.
</div>
""", unsafe_allow_html=True)

    # ── Geographic delivery (expander) ────────────────────────────────────
    if geo_real is not None:
        with st.expander("Where are we slowest? — delivery by state", expanded=False):
            top_state  = geo_real.loc[geo_real["revenue"].idxmax()]
            slow_state = geo_real.loc[geo_real["avg_delivery_days"].idxmax()]
            seller_gap = geo_real.loc[
                (geo_real["customers"] / geo_real["seller_count"].clip(lower=1)).idxmax()
            ]

            gk1, gk2, gk3 = st.columns(3)
            gk1.metric(
                "Top state by revenue", top_state["state"],
                f"R${top_state['revenue']/1e6:.1f}M",
                help="State generating the most order revenue over the dataset period.",
            )
            gk2.metric(
                "Slowest deliveries", slow_state["state"],
                f"{slow_state['avg_delivery_days']:.1f} days avg",
                delta_color="inverse",
                help="State with the highest average delivery time. Usually a distant North/Northeast state with few local sellers.",
            )
            gk3.metric(
                "Biggest buyer/seller gap", seller_gap["state"],
                f"{int(seller_gap['customers'])} buyers per {int(seller_gap['seller_count'])} sellers",
                delta_color="inverse",
                help="State where buyer demand is most out of proportion with local seller supply. High gap = slow deliveries and expansion opportunity.",
            )

            col_g1, col_g2 = st.columns([3, 2])

            with col_g1:
                geo_plot = geo_real.dropna(subset=["lat", "lon"])
                log_rev  = np.log1p(geo_plot["revenue"])
                sizes    = (log_rev - log_rev.min()) / (log_rev.max() - log_rev.min()) * 36 + 10

                fig_map = go.Figure(go.Scattergeo(
                    lon=geo_plot["lon"], lat=geo_plot["lat"],
                    mode="markers",
                    customdata=np.stack([
                        geo_plot["state"], geo_plot["revenue"], geo_plot["orders"],
                        geo_plot["avg_delivery_days"], geo_plot["on_time_rate"] * 100,
                        geo_plot["avg_review_score"], geo_plot["region"],
                    ], axis=1),
                    hovertemplate=(
                        "<b>%{customdata[0]}</b>  ·  %{customdata[6]}<br>"
                        "Revenue: R$%{customdata[1]:,.0f}<br>"
                        "Orders: %{customdata[2]:,.0f}<br>"
                        "Avg delivery: %{customdata[3]:.1f} days<br>"
                        "On-time: %{customdata[4]:.1f}%<br>"
                        "Review: %{customdata[5]:.2f}★<extra></extra>"
                    ),
                    marker=dict(
                        size=sizes,
                        color=(1 - geo_plot["on_time_rate"]) * 100,
                        colorscale="RdYlGn_r",
                        cmin=0, cmax=30,
                        colorbar=dict(title="Late %", thickness=10, len=0.6),
                        line=dict(color="#09090e", width=1),
                        opacity=0.88,
                    ),
                ))
                fig_map.update_layout(**plot_layout(
                    title="Revenue by state  ·  colour = late delivery rate",
                    height=440,
                    geo=dict(
                        scope="south america", projection_type="mercator",
                        center=dict(lat=-14, lon=-52),
                        lataxis_range=[-35, 6], lonaxis_range=[-75, -32],
                        bgcolor="#09090e", landcolor="#12122a",
                        countrycolor="#2a2a40", coastlinecolor="#2a2a40",
                        showland=True, showcountries=True, showcoastlines=True,
                    ),
                ))
                st.plotly_chart(fig_map, use_container_width=True)

            with col_g2:
                geo_sorted = geo_real.sort_values("avg_delivery_days", ascending=False).head(15)
                fig_days = go.Figure(go.Bar(
                    x=geo_sorted["avg_delivery_days"],
                    y=geo_sorted["state"],
                    orientation="h",
                    marker_color=geo_sorted["avg_delivery_days"].map(
                        lambda v: "#ff6b6b" if v > 20 else ("#f5c542" if v > 12 else "#22d3a0")
                    ),
                    text=geo_sorted["avg_delivery_days"].map(lambda v: f"{v:.1f}d"),
                    textposition="auto",
                ))
                fig_days.update_layout(**plot_layout(
                    title="Slowest states",
                    height=440,
                    xaxis=dict(title="Avg days"),
                    yaxis=dict(title=""),
                ))
                st.plotly_chart(fig_days, use_container_width=True)

            st.markdown("""
<div class="callout callout-green">
<strong>Pattern:</strong> Northern and Northeastern states have the longest delivery times,
lowest review scores, and fewest sellers relative to buyer demand.
<strong>PA has 922 buyers per seller</strong> — the most underserved market.
These regions are the clearest opportunity for localised seller recruitment.
</div>
""", unsafe_allow_html=True)

    # ── Review quality deep-dive (expander) ───────────────────────────────
    if rv_distribution is not None and rv_monthly is not None:
        with st.expander("Review score deep-dive", expanded=False):
            total_reviews = int(rv_distribution["count"].sum())
            avg_score     = (rv_distribution["score"] * rv_distribution["count"]).sum() / total_reviews
            pct_5star     = rv_distribution.loc[rv_distribution["score"] == 5, "pct"].iloc[0]
            pct_1star     = rv_distribution.loc[rv_distribution["score"] == 1, "pct"].iloc[0]

            rk1, rk2, rk3, rk4 = st.columns(4)
            rk1.metric("Total reviews",  f"{total_reviews:,}")
            rk2.metric("Avg score",      f"{avg_score:.2f} / 5")
            rk3.metric("5-star share",   f"{pct_5star:.1f}%")
            rk4.metric("1-star share",   f"{pct_1star:.1f}%", delta_color="inverse")

            col_rv1, col_rv2 = st.columns([2, 3])
            with col_rv1:
                SCORE_COLORS = ["#ff2244", "#ff6b6b", "#f5c542", "#3b9eff", "#22d3a0"]
                fig_dist = go.Figure(go.Bar(
                    x=rv_distribution["score"].astype(str),
                    y=rv_distribution["count"],
                    marker_color=SCORE_COLORS,
                    text=rv_distribution["pct"].map(lambda v: f"{v:.1f}%"),
                    textposition="outside",
                    hovertemplate="Score %{x}<br>%{y:,} reviews (%{text})<extra></extra>",
                ))
                fig_dist.update_layout(**plot_layout(
                    title="Score distribution",
                    height=300, xaxis_title="Score", yaxis_title="Reviews",
                ))
                st.plotly_chart(fig_dist, use_container_width=True)

            with col_rv2:
                fig_rv = go.Figure()
                fig_rv.add_trace(go.Scatter(
                    x=rv_monthly["review_creation_month"], y=rv_monthly["avg_score"],
                    name="Avg score", mode="lines+markers",
                    line=dict(color=COLORS["retention"], width=2), marker=dict(size=4),
                ))
                fig_rv.add_trace(go.Bar(
                    x=rv_monthly["review_creation_month"], y=rv_monthly["pct_1star"],
                    name="1-star %", marker_color="rgba(255,34,68,0.30)", yaxis="y2",
                ))
                fig_rv.update_layout(**plot_layout(
                    title="Score trend & 1-star share over time",
                    height=300,
                    xaxis=dict(tickangle=-45, nticks=10),
                    yaxis=dict(title="Avg score", range=[3.0, 5.0]),
                    yaxis2=dict(title="1-star %", overlaying="y", side="right", showgrid=False),
                    legend=dict(orientation="h", y=1.18),
                ))
                st.plotly_chart(fig_rv, use_container_width=True)

            if rv_by_category is not None:
                worst = rv_by_category.loc[rv_by_category["avg_score"].idxmin()]
                best  = rv_by_category.loc[rv_by_category["avg_score"].idxmax()]
                hi1   = rv_by_category.loc[rv_by_category["pct_1star"].idxmax()]
                st.markdown(f"""
<div class="callout callout-red">
<strong>Lowest-rated category:</strong> {worst['primary_category']} — {worst['avg_score']:.2f}★ avg,
{worst['pct_1star']:.1f}% one-star across {int(worst['orders']):,} orders.
Most 1-stars: {hi1['primary_category']} at {hi1['pct_1star']:.1f}%.
Best-rated: {best['primary_category']} at {best['avg_score']:.2f}★.
</div>
""", unsafe_allow_html=True)
