import numpy as np
import streamlit as st
import plotly.graph_objects as go

from shared import plot_layout, COLORS


def render(fl_review_lateness, fl_by_category, fl_monthly, geo_real):
    st.markdown(
        '<p style="color:#22d3a0;font-size:10px;letter-spacing:.15em;'
        'text-transform:uppercase;font-family:monospace;margin:0 0 4px">Fulfillment</p>',
        unsafe_allow_html=True,
    )
    st.markdown("### Delivery performance")
    st.markdown(
        '<p class="kpi-label">Real Olist dataset · 96k delivered orders · Sep 2016 – Oct 2018</p>',
        unsafe_allow_html=True,
    )

    if fl_review_lateness is None:
        st.warning("Run `python scripts/build_olist_data.py` first.", icon="⚙️")
    else:
        w_wt = fl_monthly["orders"]
        on_time_overall    = np.average(fl_monthly["on_time_rate"],      weights=w_wt)
        avg_days_overall   = np.average(fl_monthly["avg_delivery_days"], weights=w_wt)
        avg_review_overall = np.average(fl_monthly["avg_review_score"],  weights=w_wt)
        on_time_orders     = fl_by_category["orders"].sum()

        fk1, fk2, fk3, fk4 = st.columns(4)
        fk1.metric("On-Time Rate",     f"{on_time_overall*100:.1f}%")
        fk2.metric("Avg Delivery",     f"{avg_days_overall:.1f} days")
        fk3.metric("Avg Review Score", f"{avg_review_overall:.2f} / 5")
        fk4.metric("Orders analysed",  f"{on_time_orders:,.0f}")

        st.divider()
        col_f1, col_f2 = st.columns([3, 2])

        with col_f1:
            BUCKET_COLORS = ["#22d3a0", "#f5c542", "#ff8a4c", "#ff6b6b", "#ff2244"]
            fig_lateness = go.Figure(go.Bar(
                x=fl_review_lateness["bucket"],
                y=fl_review_lateness["avg_score"],
                marker_color=BUCKET_COLORS,
                text=fl_review_lateness["avg_score"].map(lambda v: f"{v:.2f}★"),
                textposition="outside",
                customdata=fl_review_lateness["order_count"],
                hovertemplate=(
                    "<b>%{x}</b><br>Avg score: %{y:.2f}<br>"
                    "Orders: %{customdata:,}<extra></extra>"
                ),
            ))
            fig_lateness.update_layout(**plot_layout(
                title="Review Score vs Delivery Lateness",
                height=360,
                yaxis=dict(title="Avg review score", range=[1, 5.5]),
                xaxis=dict(title=""),
            ))
            st.plotly_chart(fig_lateness, use_container_width=True)
            st.markdown("""
<div class="callout callout-red">
<strong>Key insight:</strong> On-time orders average <strong>4.4★</strong>.
Orders 8–14 days late drop to <strong>~2.0★</strong>.
Every late delivery is a review bomb — and reviews directly drive repeat purchase.
Fulfillment SLA is a direct LTV lever.
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
                title="On-Time Rate & Delivery Speed",
                height=340,
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
Avg delivery improved from ~15 days in late 2016 to ~9 days by mid-2018
as the seller network matured — tracking the review score improvement directly.
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="pillar-section"></div>', unsafe_allow_html=True)
    st.markdown("### Geographic demand & delivery coverage")
    st.markdown(
        '<p class="kpi-label">Real Olist dataset · customer delivery by Brazilian state</p>',
        unsafe_allow_html=True,
    )

    if geo_real is None:
        st.warning("Run `python scripts/build_olist_data.py` first.", icon="⚙️")
    else:
        top_state  = geo_real.loc[geo_real["revenue"].idxmax()]
        slow_state = geo_real.loc[geo_real["avg_delivery_days"].idxmax()]
        late_state = geo_real.loc[(1 - geo_real["on_time_rate"]).idxmax()]
        seller_gap = geo_real.loc[
            (geo_real["customers"] / geo_real["seller_count"].clip(lower=1)).idxmax()
        ]

        gk1, gk2, gk3, gk4 = st.columns(4)
        gk1.metric("Top State by Revenue",     top_state["state"],
                   f"R${top_state['revenue']/1e6:.1f}M")
        gk2.metric("Slowest Delivery",         slow_state["state"],
                   f"{slow_state['avg_delivery_days']:.1f} days avg", delta_color="inverse")
        gk3.metric("Highest Late Rate",        late_state["state"],
                   f"{(1-late_state['on_time_rate'])*100:.1f}% late", delta_color="inverse")
        gk4.metric("Worst Buyer/Seller Ratio", seller_gap["state"],
                   f"{int(seller_gap['customers'])} buyers / {int(seller_gap['seller_count'])} sellers")

        st.divider()
        col_g1, col_g2 = st.columns([3, 2])

        with col_g1:
            geo_plot = geo_real.dropna(subset=["lat", "lon"])
            log_rev  = np.log1p(geo_plot["revenue"])
            sizes    = (log_rev - log_rev.min()) / (log_rev.max() - log_rev.min()) * 36 + 10

            fig_map = go.Figure(go.Scattergeo(
                lon=geo_plot["lon"],
                lat=geo_plot["lat"],
                mode="markers",
                customdata=np.stack([
                    geo_plot["state"],
                    geo_plot["revenue"],
                    geo_plot["orders"],
                    geo_plot["avg_delivery_days"],
                    geo_plot["on_time_rate"] * 100,
                    geo_plot["avg_review_score"],
                    geo_plot["region"],
                ], axis=1),
                hovertemplate=(
                    "<b>%{customdata[0]}</b>  ·  %{customdata[6]}<br>"
                    "Revenue: R$%{customdata[1]:,.0f}<br>"
                    "Orders: %{customdata[2]:,.0f}<br>"
                    "Avg delivery: %{customdata[3]:.1f} days<br>"
                    "On-time: %{customdata[4]:.1f}%<br>"
                    "Review: %{customdata[5]:.2f}★"
                    "<extra></extra>"
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
                title="Revenue by State  ·  colour = late delivery rate",
                height=460,
                geo=dict(
                    scope="south america",
                    projection_type="mercator",
                    center=dict(lat=-14, lon=-52),
                    lataxis_range=[-35, 6],
                    lonaxis_range=[-75, -32],
                    bgcolor="#09090e",
                    landcolor="#12122a",
                    countrycolor="#2a2a40",
                    coastlinecolor="#2a2a40",
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
                title="Avg Delivery Days by State",
                height=460,
                xaxis=dict(title="Days"),
                yaxis=dict(title=""),
            ))
            st.plotly_chart(fig_days, use_container_width=True)

        st.markdown("""
<div class="callout callout-green">
<strong>Pattern:</strong> Northern and Northeastern states (AM, RR, AC, AP) have the longest delivery times
and lowest review scores — and the fewest sellers relative to buyer demand.
<strong>PA has 922 buyers per seller</strong>, the most underserved market in the dataset.
These regions are the clearest opportunity for localised fulfilment investment.
</div>
""", unsafe_allow_html=True)
