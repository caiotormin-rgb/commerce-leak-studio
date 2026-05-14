import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from shared import plot_layout, brl


CAT_PALETTE = [
    "#7c6bff", "#22d3a0", "#f5c542", "#3b9eff", "#ff8a4c",
    "#ff6b6b", "#9b72cf", "#38bdf8",
]

REASON_COLORS = {
    "Late delivery":   "#ff5566",
    "Damaged item":    "#ff8a4c",
    "Wrong item":      "#f5c542",
    "Changed mind":    "#3b9eff",
    "Quality issue":   "#9b72cf",
    "Fraud/cancelled": "#444466",
}


def render(cf, reviews_f, returns_f, rv_by_category, fl_by_category, pay_by_category, cb_category_df):
    st.markdown("### Category performance")
    st.markdown(
        '<p class="kpi-label">Synthetic Luma data · filtered to selected period · 13 product categories</p>',
        unsafe_allow_html=True,
    )

    # ── Aggregates ────────────────────────────────────────────────────────
    cat_totals = (
        cf.groupby("category")
        .agg(revenue=("revenue", "sum"), orders=("orders", "sum"))
        .reset_index()
    )
    cat_totals["aov"]   = cat_totals["revenue"] / cat_totals["orders"].clip(lower=1)
    cat_totals["label"] = cat_totals["category"].str.replace("_", " ").str.title()
    cat_totals = cat_totals.sort_values("revenue", ascending=False)

    top_cat    = cat_totals.iloc[0]
    total_rev  = cat_totals["revenue"].sum()
    top_share  = top_cat["revenue"] / total_rev * 100

    # Growth: last 4 weeks vs prior 4
    sorted_weeks = sorted(cf["week_start"].unique())
    has_growth   = len(sorted_weeks) >= 8
    if has_growth:
        recent = cf[cf["week_start"].isin(sorted_weeks[-4:])].groupby("category")["revenue"].sum()
        prior  = cf[cf["week_start"].isin(sorted_weeks[-8:-4])].groupby("category")["revenue"].sum()
        growth = ((recent - prior) / prior.clip(lower=1) * 100).dropna()
        top_grower     = growth.idxmax()
        top_growth_pct = growth.max()

    # Returns
    cat_returns = (
        returns_f
        .groupby("category")
        .agg(returns=("returns", "sum"), refund_value=("refund_value", "sum"))
        .reset_index()
    )
    cat_orders = cf.groupby("category")["orders"].sum().reset_index()
    cat_returns = cat_returns.merge(cat_orders, on="category")
    cat_returns["return_rate"] = cat_returns["returns"] / cat_returns["orders"].clip(lower=1)
    worst_ret_idx  = cat_returns["return_rate"].idxmax() if not cat_returns.empty else None
    total_refunds  = cat_returns["refund_value"].sum()
    overall_ret    = cat_returns["returns"].sum() / cat_returns["orders"].sum() * 100

    # ── KPIs ──────────────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Top category",  top_cat["label"], f"{top_share:.0f}% of revenue")
    k2.metric("Top category AOV", f"R${top_cat['aov']:.0f}")
    if has_growth:
        k3.metric("Fastest growing",
                  top_grower.replace("_", " ").title(),
                  f"{top_growth_pct:+.0f}% vs prior 4w")
    else:
        k3.metric("Fastest growing", "—", "< 8 weeks of data")
    k4.metric("Overall return rate", f"{overall_ret:.1f}%", delta_color="inverse")

    st.divider()

    # ── Revenue mix over time ─────────────────────────────────────────────
    st.markdown("### Revenue mix over time")

    top8   = cat_totals.head(8)["category"].tolist()
    cf_top = cf[cf["category"].isin(top8)].copy()

    fig_stack = go.Figure()
    for i, cat in enumerate(top8):
        sub = cf_top[cf_top["category"] == cat].sort_values("week_start")
        fig_stack.add_trace(go.Bar(
            x=sub["week_start"],
            y=sub["revenue"],
            name=cat.replace("_", " ").title(),
            marker_color=CAT_PALETTE[i % len(CAT_PALETTE)],
        ))
    fig_stack.update_layout(**plot_layout(
        barmode="stack",
        title="Weekly revenue by category  —  top 8",
        height=320,
        legend=dict(orientation="h", y=1.15, font=dict(size=10)),
        yaxis=dict(title="Revenue (BRL)"),
    ))
    st.plotly_chart(fig_stack, use_container_width=True)

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        fig_donut = go.Figure(go.Pie(
            labels=cat_totals["label"],
            values=cat_totals["revenue"],
            hole=0.55,
            marker=dict(colors=CAT_PALETTE * 3),
            textinfo="label+percent",
            textfont=dict(size=10),
        ))
        fig_donut.update_layout(**plot_layout(
            title="Revenue share — full period",
            height=300,
            showlegend=False,
        ))
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_g2:
        if has_growth:
            growth_df = growth.reset_index()
            growth_df.columns = ["category", "growth_pct"]
            growth_df["label"] = growth_df["category"].str.replace("_", " ").str.title()
            growth_df = growth_df.sort_values("growth_pct")
            growth_df["color"] = growth_df["growth_pct"].apply(
                lambda v: "#22d3a0" if v >= 0 else "#ff5566"
            )
            fig_growth = go.Figure(go.Bar(
                x=growth_df["growth_pct"],
                y=growth_df["label"],
                orientation="h",
                marker_color=growth_df["color"],
                text=growth_df["growth_pct"].map(lambda v: f"{v:+.0f}%"),
                textposition="outside",
            ))
            fig_growth.add_vline(x=0, line_color="#2a2a40", line_width=1)
            fig_growth.update_layout(**plot_layout(
                title="Category growth  (last 4 weeks vs prior 4)",
                height=300,
                xaxis=dict(title="Revenue change %"),
                yaxis=dict(title=""),
            ))
            st.plotly_chart(fig_growth, use_container_width=True)
        else:
            st.info("Need at least 8 weeks of data to show growth comparison.", icon="📅")

    st.divider()

    # ── Returns ───────────────────────────────────────────────────────────
    st.markdown("### Returns & refunds")
    st.markdown(
        '<p class="kpi-label">Synthetic data · modeled on Olist return patterns by category and reason</p>',
        unsafe_allow_html=True,
    )

    cat_returns_plot = cat_returns.sort_values("return_rate", ascending=False).head(12).copy()
    cat_returns_plot["label"] = cat_returns_plot["category"].str.replace("_", " ").str.title()

    rk1, rk2, rk3, rk4 = st.columns(4)
    rk1.metric("Overall return rate", f"{overall_ret:.1f}%", delta_color="inverse")
    rk2.metric("Total refund value",  brl(total_refunds),    delta_color="inverse")
    if worst_ret_idx is not None:
        worst_row = cat_returns.loc[worst_ret_idx]
        rk3.metric("Highest return rate",
                   worst_row["category"].replace("_", " ").title(),
                   f"{worst_row['return_rate']*100:.1f}%",
                   delta_color="inverse")
    rk4.metric("Categories tracked", str(len(cat_returns)))

    col_r1, col_r2 = st.columns(2)

    with col_r1:
        fig_ret = go.Figure(go.Bar(
            x=cat_returns_plot["return_rate"] * 100,
            y=cat_returns_plot["label"],
            orientation="h",
            marker_color=cat_returns_plot["return_rate"].apply(
                lambda v: "#ff5566" if v > 0.08 else ("#ff8a4c" if v > 0.06 else "#f5c542")
            ),
            text=cat_returns_plot["return_rate"].map(lambda v: f"{v*100:.1f}%"),
            textposition="outside",
            customdata=cat_returns_plot["refund_value"],
            hovertemplate="%{y}<br>Return rate: %{x:.1f}%<br>Refund value: R$%{customdata:,.0f}<extra></extra>",
        ))
        fig_ret.update_layout(**plot_layout(
            title="Return rate by category",
            height=380,
            xaxis=dict(title="Return rate %"),
            yaxis=dict(title=""),
        ))
        st.plotly_chart(fig_ret, use_container_width=True)

    with col_r2:
        top5_ret_cats = cat_returns.nlargest(5, "refund_value")["category"].tolist()
        reasons_df = (
            returns_f[returns_f["category"].isin(top5_ret_cats)]
            .groupby(["category", "reason"])["returns"]
            .sum()
            .reset_index()
        )
        reasons_df["label"] = reasons_df["category"].str.replace("_", " ").str.title()

        fig_reasons = go.Figure()
        for reason, color in REASON_COLORS.items():
            sub = reasons_df[reasons_df["reason"] == reason]
            if sub.empty:
                continue
            fig_reasons.add_trace(go.Bar(
                name=reason,
                x=sub["returns"],
                y=sub["label"],
                orientation="h",
                marker_color=color,
            ))
        fig_reasons.update_layout(**plot_layout(
            barmode="stack",
            title="Return reasons — top 5 categories by refund value",
            height=380,
            xaxis=dict(title="Returns"),
            yaxis=dict(title=""),
            legend=dict(orientation="h", y=1.12, font=dict(size=10)),
        ))
        st.plotly_chart(fig_reasons, use_container_width=True)

    # ── Category health scorecard (real data) ─────────────────────────────
    if rv_by_category is not None and fl_by_category is not None:
        st.divider()
        st.markdown("### Category health scorecard")
        st.markdown(
            '<p class="kpi-label">Real Olist dataset · reviews + fulfillment + payment risk + chargeback signals</p>',
            unsafe_allow_html=True,
        )

        health = fl_by_category[
            ["primary_category", "orders", "revenue", "on_time_rate", "avg_delivery_days"]
        ].copy()
        health = health.merge(
            rv_by_category[["primary_category", "avg_score", "pct_1star"]],
            on="primary_category", how="left",
        )
        if pay_by_category is not None:
            health = health.merge(
                pay_by_category[["primary_category", "boleto_pct", "high_inst_pct"]],
                on="primary_category", how="left",
            )
        if cb_category_df is not None:
            health = health.merge(
                cb_category_df[["primary_category", "flag_rate"]],
                on="primary_category", how="left",
            )

        health = health[health["orders"] >= 50].copy()
        health["label"] = health["primary_category"].str.replace("_", " ").str.title()

        def _score(r):
            review = (r.get("avg_score", 3.5) - 1) / 4 * 40
            ontime = r.get("on_time_rate", 0.85) * 30
            fr     = r.get("flag_rate", 0.03)
            fr     = fr if not pd.isna(fr) else 0.03
            fraud  = max(0.0, (1 - fr / 0.10)) * 30
            return round(review + ontime + fraud, 1)

        health["health_score"] = health.apply(_score, axis=1)
        health = health.sort_values("health_score", ascending=False)

        col_h1, col_h2 = st.columns([3, 2])

        with col_h1:
            top_h = health.head(15)
            fig_health = go.Figure(go.Bar(
                x=top_h["health_score"],
                y=top_h["label"],
                orientation="h",
                marker_color=top_h["health_score"].apply(
                    lambda v: "#22d3a0" if v >= 75 else ("#f5c542" if v >= 60 else "#ff5566")
                ),
                text=top_h["health_score"].map(lambda v: f"{v:.0f}"),
                textposition="outside",
                customdata=top_h[["avg_score", "on_time_rate", "flag_rate"]].fillna(0).values,
                hovertemplate=(
                    "<b>%{y}</b><br>Health: %{x:.0f}<br>"
                    "Review: %{customdata[0]:.2f}★<br>"
                    "On-time: %{customdata[1]:.1%}<br>"
                    "Flag rate: %{customdata[2]:.1%}"
                    "<extra></extra>"
                ),
            ))
            fig_health.update_layout(**plot_layout(
                title="Category health score  (review 40% · on-time 30% · fraud 30%)",
                height=460,
                xaxis=dict(title="Health score", range=[0, 110]),
                yaxis=dict(title=""),
            ))
            st.plotly_chart(fig_health, use_container_width=True)

        with col_h2:
            fig_scatter = go.Figure(go.Scatter(
                x=health["on_time_rate"] * 100,
                y=health["avg_score"],
                mode="markers+text",
                text=health["label"].str.split().str[0],
                textposition="top center",
                textfont=dict(size=9, color="#6060a0"),
                marker=dict(
                    size=np.sqrt(health["orders"].clip(lower=10)) * 1.2,
                    color=health["health_score"],
                    colorscale="RdYlGn",
                    cmin=40, cmax=100,
                    colorbar=dict(title="Score", thickness=10, len=0.6),
                    line=dict(color="#09090e", width=1),
                    opacity=0.85,
                ),
                customdata=health[["label", "orders", "health_score"]].values,
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "On-time: %{x:.1f}%<br>"
                    "Avg review: %{y:.2f}★<br>"
                    "Orders: %{customdata[1]:,}<br>"
                    "Health score: %{customdata[2]:.0f}"
                    "<extra></extra>"
                ),
            ))
            fig_scatter.update_layout(**plot_layout(
                title="Review quality vs on-time rate",
                height=460,
                xaxis=dict(title="On-time delivery %"),
                yaxis=dict(title="Avg review score"),
            ))
            st.plotly_chart(fig_scatter, use_container_width=True)

        st.markdown("""
<div class="callout">
<strong>Reading the health score:</strong> Review quality (40%) + on-time delivery rate (30%) + low chargeback/fraud flag rate (30%).
Green ≥ 75 · Amber ≥ 60 · Red below 60.
Categories low on all three signals are the highest-priority for operational intervention.
</div>
""", unsafe_allow_html=True)

    else:
        st.divider()
        st.info("Run `python scripts/build_olist_data.py` to unlock the full health scorecard.", icon="⚙️")
