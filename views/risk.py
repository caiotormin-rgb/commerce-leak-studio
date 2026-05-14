import streamlit as st
import plotly.graph_objects as go

from shared import plot_layout


def render(cb_monthly_df, cb_category_df, cb_evidence_df):
    st.markdown("### Dispute & chargeback risk — order-level flagging")
    st.markdown(
        '<p class="kpi-label">Real Olist dataset · delivered orders only · 3-signal evidence model</p>',
        unsafe_allow_html=True,
    )

    st.markdown("""
<div class="callout callout-red">
<strong>How orders are flagged:</strong> An order scores one point for each of three independent
dispute signals — <strong>1-star review</strong>, <strong>delivered 7+ days late</strong>,
<strong>7+ installment payment</strong>. Orders with 2 or 3 signals are flagged as high-confidence
chargeback proxies. Merchants lose ~80% of disputes; the average loss is R$800/month.
</div>
""", unsafe_allow_html=True)

    if cb_monthly_df is None:
        st.warning("Run `python scripts/build_olist_data.py` first.", icon="⚙️")
    else:
        total_flagged   = int(cb_monthly_df["flagged_orders"].sum())
        total_at_risk   = cb_monthly_df["flagged_revenue"].sum()
        avg_flag_rate   = (cb_monthly_df["flagged_orders"].sum() /
                           cb_monthly_df["total_orders"].sum() * 100)
        avg_flagged_rev = total_at_risk / total_flagged if total_flagged else 0
        worst_cat       = cb_category_df.iloc[0]["primary_category"] if cb_category_df is not None else "—"

        ck1, ck2, ck3, ck4 = st.columns(4)
        ck1.metric("Flagged Orders",       f"{total_flagged:,}",
                   "2+ risk signals each", delta_color="inverse")
        ck2.metric("Revenue at Risk",      f"R${total_at_risk:,.0f}",
                   "across all flagged orders", delta_color="inverse")
        ck3.metric("Flag Rate",            f"{avg_flag_rate:.1f}%",
                   "of delivered orders", delta_color="inverse")
        ck4.metric("Highest-Risk Category", worst_cat)

        st.divider()
        col_cb1, col_cb2 = st.columns([3, 2])

        with col_cb1:
            fig_cb_monthly = go.Figure()
            fig_cb_monthly.add_trace(go.Bar(
                x=cb_monthly_df["purchase_month"],
                y=cb_monthly_df["flagged_orders"],
                name="Flagged orders",
                marker_color="rgba(255,85,102,0.7)",
                hovertemplate="%{x}<br>%{y} flagged orders<extra></extra>",
            ))
            fig_cb_monthly.add_trace(go.Scatter(
                x=cb_monthly_df["purchase_month"],
                y=cb_monthly_df["flagged_revenue"],
                name="Revenue at risk (BRL)",
                mode="lines+markers",
                line=dict(color="#f5c542", width=2),
                marker=dict(size=5),
                yaxis="y2",
            ))
            fig_cb_monthly.update_layout(**plot_layout(
                title="Monthly flagged orders and revenue at risk",
                height=340,
                yaxis=dict(title="Flagged orders"),
                yaxis2=dict(title="Revenue at risk (BRL)", overlaying="y",
                            side="right", showgrid=False),
                legend=dict(orientation="h", y=1.15),
            ))
            st.plotly_chart(fig_cb_monthly, use_container_width=True)

        with col_cb2:
            if cb_evidence_df is not None:
                score_labels = {0: "No signals", 1: "1 signal", 2: "2 signals ⚠", 3: "All 3 signals 🚨"}
                ev = cb_evidence_df.copy()
                ev["label"]     = ev["risk_score"].map(score_labels)
                ev["revenue_m"] = ev["revenue"] / 1e6

                bar_colors = ["#2a2a40", "#444466", "#ff8a4c", "#ff5566"]
                fig_ev = go.Figure(go.Bar(
                    x=ev["label"],
                    y=ev["orders"],
                    marker_color=bar_colors[:len(ev)],
                    text=ev["orders"].map(lambda v: f"{v:,}"),
                    textposition="outside",
                    customdata=ev["revenue_m"],
                    hovertemplate="%{x}<br>%{y:,} orders<br>R$%{customdata:.1f}M revenue<extra></extra>",
                ))
                fig_ev.update_layout(**plot_layout(
                    title="Orders by number of risk signals",
                    height=340,
                    xaxis_title="Evidence level",
                    yaxis_title="Orders",
                ))
                st.plotly_chart(fig_ev, use_container_width=True)

        if cb_category_df is not None:
            st.markdown("#### Categories with the highest dispute risk")
            col_cb3, col_cb4 = st.columns([3, 2])

            with col_cb3:
                top_cats = cb_category_df.head(15).copy()
                top_cats["label"] = top_cats["primary_category"].str.replace("_", " ").str.title()

                fig_cat_risk = go.Figure(go.Bar(
                    x=top_cats["flag_rate"] * 100,
                    y=top_cats["label"],
                    orientation="h",
                    marker_color=top_cats["flag_rate"].apply(
                        lambda v: "#ff5566" if v > 0.05 else ("#ff8a4c" if v > 0.03 else "#f5c542")
                    ),
                    text=top_cats["flag_rate"].map(lambda v: f"{v*100:.1f}%"),
                    textposition="auto",
                    customdata=top_cats["flagged_revenue"],
                    hovertemplate="%{y}<br>Flag rate: %{x:.1f}%<br>Revenue at risk: R$%{customdata:,.0f}<extra></extra>",
                ))
                fig_cat_risk.update_layout(**plot_layout(
                    title="Flag rate by category  (red > 5%, amber > 3%)",
                    height=420,
                    xaxis=dict(title="% of orders flagged"),
                    yaxis=dict(title=""),
                ))
                st.plotly_chart(fig_cat_risk, use_container_width=True)

            with col_cb4:
                top5_rev = (cb_category_df
                            .nlargest(8, "flagged_revenue")
                            [["primary_category", "flagged_revenue", "flagged_orders", "flag_rate"]]
                            .copy())
                top5_rev["flagged_revenue"]    = top5_rev["flagged_revenue"].map(lambda v: f"R${v:,.0f}")
                top5_rev["flag_rate"]          = top5_rev["flag_rate"].map(lambda v: f"{v*100:.1f}%")
                top5_rev["primary_category"]   = top5_rev["primary_category"].str.replace("_", " ").str.title()
                top5_rev.columns = ["Category", "Revenue at Risk", "Flagged Orders", "Flag Rate"]
                st.markdown("**Highest revenue at risk by category**")
                st.dataframe(top5_rev, use_container_width=True, hide_index=True)

                st.markdown("""
<div class="callout callout-red" style="margin-top:16px">
<strong>Action:</strong> Categories with both high flag rate and high revenue at risk
are the priority intervention. A pre-shipment review policy on flagged orders
in these categories is the highest-ROI first step.
</div>
""", unsafe_allow_html=True)
