"""
Categories & Risk — Insights tab 3
Which categories are healthy? Where is revenue leaking?
"""
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from shared import plot_layout, COLORS, brl


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


def render(cf, reviews_f, returns_f, rv_by_category, fl_by_category,
           pay_by_category, cb_category_df,
           pay_by_type, pay_installments, pay_by_state,
           seller_perf, seller_conc,
           cb_monthly_df, cb_evidence_df):

    # ── Aggregates ────────────────────────────────────────────────────────
    cat_totals = (
        cf.groupby("category")
        .agg(revenue=("revenue", "sum"), orders=("orders", "sum"))
        .reset_index()
    )
    cat_totals["aov"]   = cat_totals["revenue"] / cat_totals["orders"].clip(lower=1)
    cat_totals["label"] = cat_totals["category"].str.replace("_", " ").str.title()
    cat_totals = cat_totals.sort_values("revenue", ascending=False)

    cat_returns = (
        returns_f.groupby("category")
        .agg(returns=("returns", "sum"), refund_value=("refund_value", "sum"))
        .reset_index()
        .merge(cf.groupby("category")["orders"].sum().reset_index(), on="category")
    )
    cat_returns["return_rate"] = cat_returns["returns"] / cat_returns["orders"].clip(lower=1)
    total_refunds = cat_returns["refund_value"].sum()
    overall_ret   = cat_returns["returns"].sum() / cat_returns["orders"].sum() * 100

    cb_risk_total = cb_monthly_df["flagged_revenue"].sum() if cb_monthly_df is not None else 0

    # ── Takeaway ─────────────────────────────────────────────────────────
    top_cat     = cat_totals.iloc[0]
    worst_ret   = cat_returns.sort_values("return_rate", ascending=False).iloc[0]
    worst_cb    = cb_category_df.iloc[0]["primary_category"] if cb_category_df is not None else "—"

    st.markdown(f"""
<div class="callout" style="font-size:14px;line-height:1.9">
<strong>The short version:</strong>&nbsp;
<strong>{top_cat['label']}</strong> is the top revenue category.
Overall return rate is <strong>{overall_ret:.1f}%</strong>, costing {brl(total_refunds)} in refunds.
Chargeback-flagged orders put another <strong>{brl(cb_risk_total)}</strong> at risk —
concentrated in <strong>{worst_cb.replace('_', ' ').title()}</strong>.
The health scorecard below shows where to act first.
</div>
""", unsafe_allow_html=True)

    # ── KPIs ──────────────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    k1.metric(
        "Top category", top_cat["label"],
        f"{top_cat['revenue']/cat_totals['revenue'].sum()*100:.0f}% of revenue",
        help="Category generating the highest total revenue in the selected period.",
    )
    k2.metric(
        "Overall return rate", f"{overall_ret:.1f}%",
        delta_color="inverse",
        help="Returns ÷ total orders across all categories. Higher return rates erode margin and signal quality or expectations problems.",
    )
    k3.metric(
        "Total refund cost", brl(total_refunds),
        delta_color="inverse",
        help="Estimated total refund value across all returned orders in the selected period.",
    )
    k4.metric(
        "Revenue flagged for disputes", brl(cb_risk_total),
        delta_color="inverse",
        help="Orders with 2+ dispute risk signals (late delivery + 1-star review + 7+ installments). "
             "Merchants lose ~80% of payment disputes — this is the estimated exposure.",
    )

    st.divider()

    # ── Q1: Which categories are healthy? ─────────────────────────────────
    st.markdown("### Which categories are healthy?")
    st.markdown(
        '<p style="color:#8d8daf;font-size:14px;margin:-8px 0 16px">'
        "Health score combines review quality (40%), on-time delivery (30%), and low dispute rate (30%). "
        "Green ≥ 75 · Amber ≥ 60 · Red below 60."
        "</p>",
        unsafe_allow_html=True,
    )

    if fl_by_category is not None and rv_by_category is not None:
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
                    "Flag rate: %{customdata[2]:.1%}<extra></extra>"
                ),
            ))
            fig_health.update_layout(**plot_layout(
                title="Category health score  (hover for breakdown)",
                height=460,
                xaxis=dict(title="Health score", range=[0, 115]),
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
                    "Health: %{customdata[2]:.0f}<extra></extra>"
                ),
            ))
            fig_scatter.update_layout(**plot_layout(
                title="Review quality vs on-time delivery",
                height=460,
                xaxis=dict(title="On-time delivery %"),
                yaxis=dict(title="Avg review score"),
            ))
            st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("Run `python scripts/build_olist_data.py` to load the health scorecard.", icon="⚙️")

    st.divider()

    # ── Q2: Where is money leaking? ───────────────────────────────────────
    st.markdown("### Where is money leaking out?")

    col_l1, col_l2 = st.columns(2)

    with col_l1:
        st.markdown("**Returns by category**")
        cat_ret_plot = cat_returns.sort_values("return_rate", ascending=False).head(12).copy()
        cat_ret_plot["label"] = cat_ret_plot["category"].str.replace("_", " ").str.title()
        fig_ret = go.Figure(go.Bar(
            x=cat_ret_plot["return_rate"] * 100,
            y=cat_ret_plot["label"],
            orientation="h",
            marker_color=cat_ret_plot["return_rate"].apply(
                lambda v: "#ff5566" if v > 0.08 else ("#ff8a4c" if v > 0.06 else "#f5c542")
            ),
            text=cat_ret_plot["return_rate"].map(lambda v: f"{v*100:.1f}%"),
            textposition="outside",
            customdata=cat_ret_plot["refund_value"],
            hovertemplate="%{y}<br>Return rate: %{x:.1f}%<br>Refund value: R$%{customdata:,.0f}<extra></extra>",
        ))
        fig_ret.update_layout(**plot_layout(
            title="Return rate by category",
            height=380,
            xaxis=dict(title="Return rate %"),
            yaxis=dict(title=""),
        ))
        st.plotly_chart(fig_ret, use_container_width=True)

    with col_l2:
        if cb_category_df is not None:
            st.markdown("**Dispute risk by category**")
            top_cb = cb_category_df.head(12).copy()
            top_cb["label"] = top_cb["primary_category"].str.replace("_", " ").str.title()
            fig_cb = go.Figure(go.Bar(
                x=top_cb["flag_rate"] * 100,
                y=top_cb["label"],
                orientation="h",
                marker_color=top_cb["flag_rate"].apply(
                    lambda v: "#ff5566" if v > 0.05 else ("#ff8a4c" if v > 0.03 else "#f5c542")
                ),
                text=top_cb["flag_rate"].map(lambda v: f"{v*100:.1f}%"),
                textposition="outside",
                customdata=top_cb["flagged_revenue"],
                hovertemplate="%{y}<br>Flag rate: %{x:.1f}%<br>Revenue at risk: R$%{customdata:,.0f}<extra></extra>",
            ))
            fig_cb.update_layout(**plot_layout(
                title="Dispute flag rate by category",
                height=380,
                xaxis=dict(title="% of orders flagged"),
                yaxis=dict(title=""),
            ))
            st.plotly_chart(fig_cb, use_container_width=True)
        else:
            st.info("Run `python scripts/build_olist_data.py` to load dispute data.", icon="⚙️")

    st.markdown(f"""
<div class="callout callout-red">
<strong>Where to act first:</strong> Categories appearing red in both charts — high return rate
<em>and</em> high dispute flag rate — carry compounded risk: refunds now, chargebacks later.
{brl(total_refunds)} in refunds + {brl(cb_risk_total)} in dispute exposure = {brl(total_refunds + cb_risk_total)} total leakage.
</div>
""", unsafe_allow_html=True)

    st.divider()

    # ── Analyst tabs ──────────────────────────────────────────────────────
    st.markdown(
        '<p class="kpi-label" style="margin-bottom:10px">Detailed breakdowns</p>',
        unsafe_allow_html=True,
    )
    tab_sellers, tab_payments, tab_returns_detail, tab_disputes = st.tabs([
        "Sellers", "Payment risk", "Return reasons", "Dispute details",
    ])

    # ── Tab: Sellers ──────────────────────────────────────────────────────
    with tab_sellers:
        if seller_perf is None:
            st.warning("Run `python scripts/build_olist_data.py` first.", icon="⚙️")
        else:
            total_rev_s = seller_perf["revenue"].sum()
            top10_share = seller_perf.head(10)["revenue"].sum() / total_rev_s * 100
            avg_score_s = np.average(seller_perf["avg_review_score"], weights=seller_perf["orders"])

            sk1, sk2, sk3 = st.columns(3)
            sk1.metric(
                "Qualifying sellers", f"{len(seller_perf):,}",
                help="Sellers with 10+ orders in the dataset.",
            )
            sk2.metric(
                "Top 10 revenue share", f"{top10_share:.1f}%",
                help="Share of total revenue generated by the top 10 sellers. High concentration = fragility.",
            )
            sk3.metric(
                "Avg review score", f"{avg_score_s:.2f}★",
                help="Order-weighted average review score across all qualifying sellers.",
            )

            col_s1, col_s2 = st.columns([3, 2])
            with col_s1:
                fig_s = px.scatter(
                    seller_perf.head(200),
                    x="revenue", y="avg_review_score",
                    size="orders", color="on_time_rate",
                    color_continuous_scale="RdYlGn",
                    hover_name="seller_id",
                    hover_data={
                        "seller_state": True, "top_category": True,
                        "orders": ":,", "revenue": ":,.0f",
                        "on_time_rate": ":.1%", "avg_review_score": ":.2f",
                    },
                    labels={
                        "revenue": "Revenue (BRL)",
                        "avg_review_score": "Avg review score",
                        "on_time_rate": "On-time",
                    },
                    size_max=30,
                )
                fig_s.update_layout(**plot_layout(
                    title="Revenue vs review score  (top 200 sellers · colour = on-time rate)",
                    height=400,
                    coloraxis_colorbar=dict(title="On-time", tickformat=".0%", thickness=10),
                ))
                st.plotly_chart(fig_s, use_container_width=True)

            with col_s2:
                fig_pareto = go.Figure(go.Scatter(
                    x=list(range(1, len(seller_conc) + 1)),
                    y=seller_conc["cumulative_revenue_pct"],
                    mode="lines", fill="tozeroy",
                    fillcolor="rgba(124,107,255,0.15)",
                    line=dict(color=COLORS["attribution"], width=2),
                    hovertemplate="Top %{x} sellers<br>%{y:.1f}% of revenue<extra></extra>",
                ))
                fig_pareto.add_hline(y=80, line_dash="dot",
                    line_color="#f5c542", annotation_text="80%",
                    annotation_position="right")
                fig_pareto.update_layout(**plot_layout(
                    title="How many sellers drive 80% of revenue",
                    height=400,
                    xaxis=dict(title="Seller rank"),
                    yaxis=dict(title="Cumulative revenue %", range=[0, 101]),
                ))
                st.plotly_chart(fig_pareto, use_container_width=True)

            with st.expander("Worst-rated sellers (min 50 orders)"):
                worst = (
                    seller_perf[seller_perf["orders"] >= 50]
                    .nsmallest(12, "avg_review_score")
                    [["seller_id", "seller_state", "top_category", "orders",
                      "revenue", "on_time_rate", "avg_review_score"]]
                    .copy()
                )
                worst["revenue"]          = worst["revenue"].map(lambda v: f"R${v:,.0f}")
                worst["on_time_rate"]     = worst["on_time_rate"].map(lambda v: f"{v*100:.1f}%")
                worst["avg_review_score"] = worst["avg_review_score"].map(lambda v: f"{v:.2f}★")
                worst["seller_id"]        = worst["seller_id"].str[:12] + "…"
                st.dataframe(worst, use_container_width=True, hide_index=True)

    # ── Tab: Payment risk ──────────────────────────────────────────────────
    with tab_payments:
        if pay_by_type is None:
            st.warning("Run `python scripts/build_olist_data.py` first.", icon="⚙️")
        else:
            cc_row  = pay_by_type[pay_by_type["payment_type"] == "credit_card"].iloc[0]
            bol_row = pay_by_type[pay_by_type["payment_type"] == "boleto"].iloc[0]
            total_ord = pay_by_type["orders"].sum()
            high_inst = pay_installments.loc[pay_installments["cancellation_rate"].idxmax()]

            pk1, pk2, pk3 = st.columns(3)
            pk1.metric(
                "Credit card share", f"{cc_row['orders']/total_ord*100:.0f}%",
                help="Credit card = lower settlement risk than boleto.",
            )
            pk2.metric(
                "Boleto share", f"{bol_row['orders']/total_ord*100:.0f}%",
                help="Boleto = bank slip paid separately. Higher non-payment risk than credit card.",
            )
            pk3.metric(
                "Highest-risk installment bucket", high_inst["installment_bucket"],
                f"{high_inst['cancellation_rate']*100:.1f}% cancel rate",
                delta_color="inverse",
                help="Installment bucket (number of monthly payments) with the highest cancellation rate.",
            )

            col_pk1, col_pk2 = st.columns(2)
            with col_pk1:
                TYPE_LABELS = {
                    "credit_card": "Credit Card", "boleto": "Boleto",
                    "voucher": "Voucher", "debit_card": "Debit Card",
                }
                pbt = pay_by_type.copy()
                pbt["label"] = pbt["payment_type"].map(TYPE_LABELS).fillna(pbt["payment_type"])
                fig_pt = go.Figure()
                fig_pt.add_trace(go.Bar(
                    name="Orders", x=pbt["label"], y=pbt["orders"],
                    marker_color=COLORS["geo"],
                    text=pbt["orders"].map(lambda v: f"{v:,}"),
                    textposition="outside",
                ))
                fig_pt.add_trace(go.Scatter(
                    name="Cancel rate", x=pbt["label"],
                    y=pbt["cancellation_rate"] * 100,
                    mode="markers",
                    marker=dict(color=COLORS["claimed"], size=14, symbol="diamond"),
                    yaxis="y2",
                ))
                fig_pt.update_layout(**plot_layout(
                    title="Orders and cancel rate by payment type",
                    height=320,
                    yaxis=dict(title="Orders"),
                    yaxis2=dict(title="Cancel %", overlaying="y", side="right", showgrid=False),
                    legend=dict(orientation="h", y=1.15),
                ))
                st.plotly_chart(fig_pt, use_container_width=True)

            with col_pk2:
                pi = pay_installments.copy()
                fig_inst = go.Figure()
                fig_inst.add_trace(go.Bar(
                    name="Orders", x=pi["installment_bucket"], y=pi["orders"],
                    marker_color="#9b72cf",
                    text=pi["orders"].map(lambda v: f"{v:,}"),
                    textposition="outside",
                ))
                fig_inst.add_trace(go.Scatter(
                    name="Cancel rate",
                    x=pi["installment_bucket"], y=pi["cancellation_rate"] * 100,
                    mode="lines+markers",
                    line=dict(color=COLORS["claimed"], width=2),
                    marker=dict(size=8),
                    yaxis="y2",
                ))
                fig_inst.update_layout(**plot_layout(
                    title="Cancel rate by number of installments",
                    height=320,
                    yaxis=dict(title="Orders"),
                    yaxis2=dict(title="Cancel %", overlaying="y", side="right", showgrid=False),
                    legend=dict(orientation="h", y=1.15),
                ))
                st.plotly_chart(fig_inst, use_container_width=True)

            st.markdown("""
<div class="callout callout-red">
<strong>Risk signal:</strong> Orders split across 13–24 installments have the highest cancellation rate.
High-installment boleto orders carry dual risk: payment may not settle, and the customer is locked
into a long repayment window. These orders warrant additional verification before shipping.
</div>
""", unsafe_allow_html=True)

    # ── Tab: Return reasons ────────────────────────────────────────────────
    with tab_returns_detail:
        st.markdown("**Revenue mix over time — where are returns concentrated?**")

        top8   = cat_totals.head(8)["category"].tolist()
        fig_stack = go.Figure()
        for i, cat in enumerate(top8):
            sub = cf[cf["category"] == cat].sort_values("week_start")
            fig_stack.add_trace(go.Bar(
                x=sub["week_start"], y=sub["revenue"],
                name=cat.replace("_", " ").title(),
                marker_color=CAT_PALETTE[i % len(CAT_PALETTE)],
            ))
        fig_stack.update_layout(**plot_layout(
            barmode="stack", title="Weekly revenue by category — top 8",
            height=300, legend=dict(orientation="h", y=1.15, font=dict(size=10)),
            yaxis=dict(title="Revenue (BRL)"),
        ))
        st.plotly_chart(fig_stack, use_container_width=True)

        col_ret1, col_ret2 = st.columns(2)
        with col_ret1:
            top5_ret = cat_returns.nlargest(5, "refund_value")["category"].tolist()
            reasons_df = (
                returns_f[returns_f["category"].isin(top5_ret)]
                .groupby(["category", "reason"])["returns"]
                .sum().reset_index()
            )
            reasons_df["label"] = reasons_df["category"].str.replace("_", " ").str.title()
            fig_reasons = go.Figure()
            for reason, color in REASON_COLORS.items():
                sub = reasons_df[reasons_df["reason"] == reason]
                if sub.empty:
                    continue
                fig_reasons.add_trace(go.Bar(
                    name=reason, x=sub["returns"], y=sub["label"],
                    orientation="h", marker_color=color,
                ))
            fig_reasons.update_layout(**plot_layout(
                barmode="stack",
                title="Return reasons — top 5 categories by refund value",
                height=320,
                xaxis=dict(title="Returns"),
                yaxis=dict(title=""),
                legend=dict(orientation="h", y=1.12, font=dict(size=10)),
            ))
            st.plotly_chart(fig_reasons, use_container_width=True)

        with col_ret2:
            col_d1, col_d2 = st.columns(2)
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
                height=320, showlegend=False,
            ))
            st.plotly_chart(fig_donut, use_container_width=True)

    # ── Tab: Dispute details ───────────────────────────────────────────────
    with tab_disputes:
        if cb_monthly_df is None:
            st.warning("Run `python scripts/build_olist_data.py` first.", icon="⚙️")
        else:
            total_flagged = int(cb_monthly_df["flagged_orders"].sum())
            avg_flag_rate = (
                cb_monthly_df["flagged_orders"].sum() /
                cb_monthly_df["total_orders"].sum() * 100
            )

            dk1, dk2, dk3 = st.columns(3)
            dk1.metric(
                "Flagged orders", f"{total_flagged:,}",
                "2+ risk signals each",
                delta_color="inverse",
                help="Orders with at least 2 of 3 dispute signals: 1-star review, 7+ days late, 7+ installment payment.",
            )
            dk2.metric(
                "Revenue at risk", brl(cb_risk_total),
                delta_color="inverse",
                help="Total order value across flagged orders. Merchants lose ~80% of payment disputes.",
            )
            dk3.metric(
                "Flag rate", f"{avg_flag_rate:.1f}%",
                "of delivered orders",
                delta_color="inverse",
            )

            col_cb1, col_cb2 = st.columns([3, 2])
            with col_cb1:
                fig_cbm = go.Figure()
                fig_cbm.add_trace(go.Bar(
                    x=cb_monthly_df["purchase_month"],
                    y=cb_monthly_df["flagged_orders"],
                    name="Flagged orders",
                    marker_color="rgba(255,85,102,0.7)",
                ))
                fig_cbm.add_trace(go.Scatter(
                    x=cb_monthly_df["purchase_month"],
                    y=cb_monthly_df["flagged_revenue"],
                    name="Revenue at risk (BRL)",
                    mode="lines+markers",
                    line=dict(color="#f5c542", width=2),
                    marker=dict(size=5),
                    yaxis="y2",
                ))
                fig_cbm.update_layout(**plot_layout(
                    title="Flagged orders and revenue at risk — monthly",
                    height=300,
                    yaxis=dict(title="Flagged orders"),
                    yaxis2=dict(title="Revenue at risk (BRL)", overlaying="y",
                                side="right", showgrid=False),
                    legend=dict(orientation="h", y=1.15),
                ))
                st.plotly_chart(fig_cbm, use_container_width=True)

            with col_cb2:
                if cb_evidence_df is not None:
                    score_labels = {
                        0: "No signals", 1: "1 signal",
                        2: "2 signals ⚠", 3: "All 3 signals 🚨",
                    }
                    ev = cb_evidence_df.copy()
                    ev["label"] = ev["risk_score"].map(score_labels)
                    bar_colors  = ["#2a2a40", "#444466", "#ff8a4c", "#ff5566"]
                    fig_ev = go.Figure(go.Bar(
                        x=ev["label"], y=ev["orders"],
                        marker_color=bar_colors[:len(ev)],
                        text=ev["orders"].map(lambda v: f"{v:,}"),
                        textposition="outside",
                        customdata=ev["revenue"] / 1e6,
                        hovertemplate="%{x}<br>%{y:,} orders<br>R$%{customdata:.1f}M revenue<extra></extra>",
                    ))
                    fig_ev.update_layout(**plot_layout(
                        title="Orders by number of risk signals",
                        height=300,
                        xaxis_title="Evidence level",
                        yaxis_title="Orders",
                    ))
                    st.plotly_chart(fig_ev, use_container_width=True)

            if cb_category_df is not None:
                top5_rev = (
                    cb_category_df.nlargest(8, "flagged_revenue")
                    [["primary_category", "flagged_revenue", "flagged_orders", "flag_rate"]]
                    .copy()
                )
                top5_rev["flagged_revenue"]  = top5_rev["flagged_revenue"].map(lambda v: f"R${v:,.0f}")
                top5_rev["flag_rate"]        = top5_rev["flag_rate"].map(lambda v: f"{v*100:.1f}%")
                top5_rev["primary_category"] = top5_rev["primary_category"].str.replace("_", " ").str.title()
                top5_rev.columns = ["Category", "Revenue at Risk", "Flagged Orders", "Flag Rate"]
                st.markdown("**Highest revenue at risk by category**")
                st.dataframe(top5_rev, use_container_width=True, hide_index=True)
