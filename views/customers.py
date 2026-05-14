import streamlit as st
import plotly.graph_objects as go

from shared import plot_layout, COLORS


def render(cohorts_real, rv_distribution, rv_monthly, rv_by_category):
    st.markdown(
        '<p style="color:#f5c542;font-size:10px;letter-spacing:.15em;'
        'text-transform:uppercase;font-family:monospace;margin:0 0 4px">Retention</p>',
        unsafe_allow_html=True,
    )
    st.markdown("### Cohort retention & LTV")
    st.markdown(
        '<p class="kpi-label">Real Olist dataset · 96k customers · true repeat-purchase retention</p>',
        unsafe_allow_html=True,
    )

    if cohorts_real is None:
        st.warning("Run `python scripts/build_olist_data.py` first.", icon="⚙️")
    else:
        overall_repeat  = (cohorts_real["ret_180d"] * cohorts_real["cohort_size"]).sum() / cohorts_real["cohort_size"].sum()
        avg_ltv_180     = cohorts_real["ltv_180d"].mean()
        total_customers = int(cohorts_real["cohort_size"].sum())
        n_outliers      = int(cohorts_real["is_outlier"].sum())

        ck1, ck2, ck3, ck4 = st.columns(4)
        ck1.metric("Total Acquired",   f"{total_customers:,}")
        ck2.metric("180d Repeat Rate", f"{overall_repeat*100:.1f}%", delta_color="inverse")
        ck3.metric("Avg LTV (180d)",   f"R${avg_ltv_180:.0f}")
        ck4.metric("Low-Retention Cohorts", str(n_outliers),
                   "flagged outliers", delta_color="inverse")

        st.markdown("""
<div class="callout callout-amber">
<strong>The retention problem:</strong> Only <strong>2.1% of customers</strong> placed a second
order within 180 days. Acquisition is not compounding into repeat revenue.
LTV grows almost entirely from first-order value, not from loyalty.
This makes CAC payback entirely dependent on first-order margin.
</div>
""", unsafe_allow_html=True)

        col_c1, col_c2 = st.columns([3, 2])

        with col_c1:
            hm = cohorts_real[["cohort_month", "ret_30d", "ret_60d", "ret_90d", "ret_180d"]].set_index("cohort_month") * 100
            hm.columns = ["30d", "60d", "90d", "180d"]

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
                hovertemplate="Cohort: %{y}<br>Period: %{x}<br>Retention: %{z:.1f}%<extra></extra>",
            ))
            for i, row in enumerate(cohorts_real.itertuples()):
                if row.is_outlier:
                    fig_hm.add_shape(type="rect",
                        x0=-0.5, x1=3.5, y0=i-0.5, y1=i+0.5,
                        line=dict(color="#ff5566", width=2))
                    fig_hm.add_annotation(x=3.6, y=i, text="⚠", showarrow=False,
                        font=dict(color="#ff5566", size=11), xanchor="left")

            fig_hm.update_layout(**plot_layout(
                title="Customers who bought again  ·  % who placed a 2nd order within X days",
                height=500,
                xaxis=dict(side="top"),
            ))
            st.plotly_chart(fig_hm, use_container_width=True)

        with col_c2:
            fig_ltv = go.Figure()
            for _, row in cohorts_real.iterrows():
                color   = "#ff5566" if row["is_outlier"] else COLORS["retention"]
                opacity = 1.0 if row["is_outlier"] else 0.25
                width   = 2.0 if row["is_outlier"] else 0.8
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
                name="Median LTV",
                mode="lines+markers",
                line=dict(color=COLORS["retention"], width=2.5, dash="dash"),
                marker=dict(size=6),
            ))
            fig_ltv.update_layout(**plot_layout(
                title="LTV per Acquired Customer",
                height=280,
                xaxis=dict(title="Days since acquisition", tickvals=[30, 60, 90, 180]),
                yaxis=dict(title="LTV (BRL)"),
                legend=dict(orientation="h", y=1.15),
            ))
            st.plotly_chart(fig_ltv, use_container_width=True)

    st.markdown('<div class="pillar-section"></div>', unsafe_allow_html=True)
    st.markdown("### Customer review quality")
    st.markdown(
        '<p class="kpi-label">Real Olist dataset · 104k reviews · Sep 2016 – Oct 2018</p>',
        unsafe_allow_html=True,
    )

    if rv_distribution is None:
        st.warning("Run `python scripts/build_olist_data.py` first.", icon="⚙️")
    else:
        total_reviews = int(rv_distribution["count"].sum())
        avg_score     = (rv_distribution["score"] * rv_distribution["count"]).sum() / total_reviews
        pct_5star     = rv_distribution.loc[rv_distribution["score"] == 5, "pct"].iloc[0]
        pct_1star     = rv_distribution.loc[rv_distribution["score"] == 1, "pct"].iloc[0]

        rk1, rk2, rk3, rk4 = st.columns(4)
        rk1.metric("Total Reviews", f"{total_reviews:,}")
        rk2.metric("Avg Score",     f"{avg_score:.2f} / 5")
        rk3.metric("5-Star Share",  f"{pct_5star:.1f}%")
        rk4.metric("1-Star Share",  f"{pct_1star:.1f}%", delta_color="inverse")

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
                title="Score Distribution",
                height=320,
                xaxis_title="Score",
                yaxis_title="Reviews",
            ))
            st.plotly_chart(fig_dist, use_container_width=True)

        with col_rv2:
            fig_rv_trend = go.Figure()
            fig_rv_trend.add_trace(go.Scatter(
                x=rv_monthly["review_creation_month"],
                y=rv_monthly["avg_score"],
                name="Avg score",
                mode="lines+markers",
                line=dict(color=COLORS["retention"], width=2),
                marker=dict(size=4),
            ))
            fig_rv_trend.add_trace(go.Bar(
                x=rv_monthly["review_creation_month"],
                y=rv_monthly["pct_1star"],
                name="1-star %",
                marker_color="rgba(255,34,68,0.30)",
                yaxis="y2",
            ))
            fig_rv_trend.update_layout(**plot_layout(
                title="Score Trend & 1-Star Share",
                height=320,
                xaxis=dict(tickangle=-45, nticks=10),
                yaxis=dict(title="Avg score", range=[3.0, 5.0]),
                yaxis2=dict(title="1-star %", overlaying="y", side="right", showgrid=False),
                legend=dict(orientation="h", y=1.18),
            ))
            st.plotly_chart(fig_rv_trend, use_container_width=True)

        if rv_by_category is not None:
            worst_cat_row = rv_by_category.loc[rv_by_category["avg_score"].idxmin()]
            best_cat_row  = rv_by_category.loc[rv_by_category["avg_score"].idxmax()]
            high_1star    = rv_by_category.loc[rv_by_category["pct_1star"].idxmax()]
            st.markdown(f"""
<div class="callout callout-red">
<strong>Lowest-rated category:</strong> {worst_cat_row['primary_category']}
— {worst_cat_row['avg_score']:.2f}★ avg, {worst_cat_row['pct_1star']:.1f}% one-star
across {int(worst_cat_row['orders']):,} orders.
Most dissatisfied: {high_1star['primary_category']} at {high_1star['pct_1star']:.1f}% one-star.
Best-rated: {best_cat_row['primary_category']} at {best_cat_row['avg_score']:.2f}★.
</div>
""", unsafe_allow_html=True)
