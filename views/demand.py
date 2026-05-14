import streamlit as st
import plotly.graph_objects as go

from shared import plot_layout, MONTH_NAMES


def render(season_monthly, season_cat_monthly):
    st.markdown("### Seasonal demand patterns")
    st.markdown(
        '<p class="kpi-label">Real Olist dataset · Sep 2016 – Oct 2018 · delivered orders</p>',
        unsafe_allow_html=True,
    )

    if season_monthly is None:
        st.warning("Run `python scripts/build_olist_data.py` first.", icon="⚙️")
    else:
        sm = season_monthly.copy()
        sm["month_name"] = sm["month_num"].apply(lambda m: MONTH_NAMES[m - 1])

        # ── KPIs ──────────────────────────────────────────────────────────
        peak_row   = sm.loc[sm["orders"].idxmax()]
        trough_row = sm.loc[sm["orders"].idxmin()]
        peak_ratio = peak_row["orders"] / trough_row["orders"]

        y17 = sm[sm["year"] == 2017].set_index("month_num")["orders"]
        y18 = sm[sm["year"] == 2018].set_index("month_num")["orders"]
        shared_months = y17.index.intersection(y18.index)
        yoy_growth = (y18[shared_months].sum() / y17[shared_months].sum() - 1) * 100 if len(shared_months) else 0

        sn1, sn2, sn3, sn4 = st.columns(4)
        sn1.metric("Peak Month",    peak_row["purchase_month"],
                   f"{peak_row['orders']:,} orders")
        sn2.metric("Trough Month",  trough_row["purchase_month"],
                   f"{trough_row['orders']:,} orders")
        sn3.metric("Peak / Trough", f"{peak_ratio:.1f}×",
                   "seasonal amplitude")
        sn4.metric("YoY Growth (shared months)", f"{yoy_growth:+.1f}%",
                   "2018 vs 2017")

        st.divider()

        sm = sm.sort_values("purchase_month").reset_index(drop=True)
        sm["trend"]     = sm["orders"].rolling(3, center=True, min_periods=2).mean()
        sm["detrended"] = sm["orders"] - sm["trend"]

        fig_trend = go.Figure()
        fig_trend.add_trace(go.Bar(
            x=sm["purchase_month"], y=sm["orders"],
            name="Monthly orders",
            marker_color="rgba(59,158,255,0.4)",
        ))
        fig_trend.add_trace(go.Scatter(
            x=sm["purchase_month"], y=sm["trend"],
            name="Trend (3-mo avg)",
            mode="lines",
            line=dict(color="#3b9eff", width=2.5),
        ))
        fig_trend.add_annotation(
            x=peak_row["purchase_month"], y=peak_row["orders"],
            text=f"Peak: {int(peak_row['orders']):,}",
            showarrow=True, arrowhead=2,
            font=dict(color="#f5c542", size=10),
            bgcolor="rgba(0,0,0,0.5)",
            arrowcolor="#f5c542",
            ay=-30,
        )
        fig_trend.update_layout(**plot_layout(
            title="Monthly Orders with Trend Decomposition",
            height=320,
            yaxis=dict(title="Orders"),
            legend=dict(orientation="h", y=1.15),
        ))
        st.plotly_chart(fig_trend, use_container_width=True)

        col_s1, col_s2 = st.columns(2)

        with col_s1:
            month_avg   = sm.groupby("month_num")["orders"].mean()
            overall_avg = sm["orders"].mean()
            indices = (month_avg / overall_avg * 100).reset_index()
            indices.columns = ["month_num", "index"]
            indices["month_name"] = indices["month_num"].apply(lambda m: MONTH_NAMES[m - 1])
            indices["color"] = indices["index"].apply(
                lambda v: "#f5c542" if v >= 100 else "#3b9eff"
            )

            fig_idx = go.Figure(go.Bar(
                x=indices["month_name"],
                y=indices["index"],
                marker_color=indices["color"],
                text=indices["index"].map(lambda v: f"{v:.0f}"),
                textposition="outside",
                hovertemplate="%{x}<br>Seasonal index: %{y:.1f}<extra></extra>",
            ))
            fig_idx.add_hline(y=100, line_dash="dot", line_color="#2a2a40",
                              annotation_text="baseline 100",
                              annotation_font_color="#5a5a78",
                              annotation_position="right")
            fig_idx.update_layout(**plot_layout(
                title="Seasonal Index by Month  (100 = average)",
                height=300,
                yaxis=dict(title="Index", range=[50, 160]),
                xaxis=dict(title=""),
            ))
            st.plotly_chart(fig_idx, use_container_width=True)

        with col_s2:
            YEAR_COLORS = {2016: "#9b72cf", 2017: "#3b9eff", 2018: "#22d3a0"}
            fig_yoy = go.Figure()
            for yr, grp in sm.groupby("year"):
                grp = grp.sort_values("month_num")
                fig_yoy.add_trace(go.Scatter(
                    x=grp["month_name"],
                    y=grp["orders"],
                    name=str(yr),
                    mode="lines+markers",
                    line=dict(color=YEAR_COLORS.get(yr, "#888899"), width=2),
                    marker=dict(size=5),
                    opacity=0.5 if yr == 2016 else 1.0,
                ))
            fig_yoy.update_layout(**plot_layout(
                title="Year-over-Year Orders  (2016 partial)",
                height=300,
                xaxis=dict(title="Month", categoryorder="array",
                           categoryarray=MONTH_NAMES),
                yaxis=dict(title="Orders"),
                legend=dict(orientation="h", y=1.15),
            ))
            st.plotly_chart(fig_yoy, use_container_width=True)

        if season_cat_monthly is not None:
            scm  = season_cat_monthly.copy()
            top5 = scm.groupby("primary_category")["orders"].sum().nlargest(5).index
            scm  = scm[scm["primary_category"].isin(top5)]
            CAT_COLORS = ["#7c6bff", "#22d3a0", "#f5c542", "#3b9eff", "#ff8a4c"]

            fig_catmix = go.Figure()
            for i, cat in enumerate(top5):
                sub = scm[scm["primary_category"] == cat].sort_values("purchase_month")
                fig_catmix.add_trace(go.Bar(
                    x=sub["purchase_month"],
                    y=sub["orders"],
                    name=cat,
                    marker_color=CAT_COLORS[i % len(CAT_COLORS)],
                ))
            fig_catmix.update_layout(**plot_layout(
                barmode="stack",
                title="Which categories drive demand each month  —  top 5",
                height=280,
                legend=dict(orientation="h", y=1.15, font=dict(size=10)),
                yaxis=dict(title="Orders"),
            ))
            st.plotly_chart(fig_catmix, use_container_width=True)

        st.markdown("""
<div class="callout">
<strong>Reading this:</strong> The seasonal index shows which months historically over- or under-perform
the annual average — useful for planning spend allocation before peak periods.
The year-over-year chart shows whether last year's pattern is repeating this year.
</div>
""", unsafe_allow_html=True)
