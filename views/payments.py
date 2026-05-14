import streamlit as st
import plotly.graph_objects as go

from shared import plot_layout, COLORS


def render(pay_by_type, pay_installments, pay_by_category, pay_by_state):
    st.markdown("### Payment mix & cancellation risk")
    st.markdown(
        '<p class="kpi-label">Real Olist dataset · 99k orders · payment type, installments, cancellations</p>',
        unsafe_allow_html=True,
    )

    if pay_by_type is None:
        st.warning("Run `python scripts/build_olist_data.py` first.", icon="⚙️")
    else:
        cc_row    = pay_by_type[pay_by_type["payment_type"] == "credit_card"].iloc[0]
        bol_row   = pay_by_type[pay_by_type["payment_type"] == "boleto"].iloc[0]
        total_ord = pay_by_type["orders"].sum()
        total_can = pay_by_type["cancelled"].sum()
        high_inst = pay_installments.loc[pay_installments["cancellation_rate"].idxmax()]

        pk1, pk2, pk3, pk4 = st.columns(4)
        pk1.metric("Credit Card Share",   f"{cc_row['orders']/total_ord*100:.0f}%")
        pk2.metric("Boleto Share",        f"{bol_row['orders']/total_ord*100:.0f}%")
        pk3.metric("Overall Cancel Rate", f"{total_can/total_ord*100:.1f}%", delta_color="inverse")
        pk4.metric("Highest-Risk Bucket", high_inst["installment_bucket"],
                   f"{high_inst['cancellation_rate']*100:.1f}% cancel rate", delta_color="inverse")

        st.divider()
        col_pk1, col_pk2 = st.columns(2)

        with col_pk1:
            TYPE_LABELS = {
                "credit_card": "Credit Card",
                "boleto": "Boleto",
                "voucher": "Voucher",
                "debit_card": "Debit Card",
            }
            pbt = pay_by_type.copy()
            pbt["label"] = pbt["payment_type"].map(TYPE_LABELS).fillna(pbt["payment_type"])
            fig_paytype = go.Figure()
            fig_paytype.add_trace(go.Bar(
                name="Orders",
                x=pbt["label"], y=pbt["orders"],
                marker_color=COLORS["geo"],
                text=pbt["orders"].map(lambda v: f"{v:,}"),
                textposition="outside",
            ))
            fig_paytype.add_trace(go.Scatter(
                name="Cancel rate",
                x=pbt["label"], y=pbt["cancellation_rate"] * 100,
                mode="markers",
                marker=dict(color=COLORS["claimed"], size=14, symbol="diamond"),
                yaxis="y2",
            ))
            fig_paytype.update_layout(**plot_layout(
                title="Orders & Cancel Rate by Payment Type",
                height=360,
                yaxis=dict(title="Orders"),
                yaxis2=dict(title="Cancel %", overlaying="y", side="right", showgrid=False),
                legend=dict(orientation="h", y=1.15),
            ))
            st.plotly_chart(fig_paytype, use_container_width=True)

        with col_pk2:
            pi = pay_installments.copy()
            fig_inst = go.Figure()
            fig_inst.add_trace(go.Bar(
                name="Orders",
                x=pi["installment_bucket"], y=pi["orders"],
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
                title="Orders & Cancel Rate by Installment Count",
                height=360,
                yaxis=dict(title="Orders"),
                yaxis2=dict(title="Cancel %", overlaying="y", side="right", showgrid=False),
                legend=dict(orientation="h", y=1.15),
            ))
            st.plotly_chart(fig_inst, use_container_width=True)

        st.markdown("""
<div class="callout callout-red">
<strong>Risk signal:</strong> Orders split across 13–24 installments have the highest cancellation rate
in the dataset. High-installment boleto orders carry dual risk: payment may not settle, and the
customer is committed to a long repayment window. These orders warrant additional fulfilment
verification before shipping.
</div>
""", unsafe_allow_html=True)

        st.divider()
        st.markdown("### Which categories are most exposed to risky payment methods")
        st.markdown('<p class="kpi-label">Boleto = higher non-payment risk &nbsp;·&nbsp; 7x+ installments = higher cancellation risk</p>', unsafe_allow_html=True)

        if pay_by_category is not None:
            pbc = pay_by_category.copy()
            pbc["risk_score"] = pbc["boleto_pct"] * 0.6 + pbc["high_inst_pct"] * 0.4
            pbc = pbc[pbc["total_orders"] >= 50].sort_values("risk_score", ascending=True).tail(20)
            pbc["label"] = pbc["primary_category"].str.replace("_", " ").str.title()

            fig_cat_pay = go.Figure()
            fig_cat_pay.add_trace(go.Bar(
                name="Boleto %",
                y=pbc["label"],
                x=pbc["boleto_pct"] * 100,
                orientation="h",
                marker_color="#ff5566",
                text=pbc["boleto_pct"].map(lambda v: f"{v*100:.0f}%"),
                textposition="inside",
                insidetextanchor="middle",
            ))
            fig_cat_pay.add_trace(go.Bar(
                name="High installments (7x+) %",
                y=pbc["label"],
                x=pbc["high_inst_pct"] * 100,
                orientation="h",
                marker_color="#f5c542",
                text=pbc["high_inst_pct"].map(lambda v: f"{v*100:.0f}%"),
                textposition="inside",
                insidetextanchor="middle",
            ))
            fig_cat_pay.update_layout(**plot_layout(
                title="Top 20 categories by payment risk exposure",
                height=540,
                barmode="stack",
                xaxis=dict(title="% of orders", ticksuffix="%"),
                yaxis=dict(title=""),
                legend=dict(orientation="h", y=1.06),
            ))
            st.plotly_chart(fig_cat_pay, use_container_width=True)

            top_boleto = pbc.sort_values("boleto_pct", ascending=False).iloc[0]
            top_inst   = pbc.sort_values("high_inst_pct", ascending=False).iloc[0]
            st.markdown(f"""
<div class="callout callout-amber">
<strong>{top_boleto["label"]}</strong> has the highest boleto dependency at {top_boleto["boleto_pct"]*100:.0f}% of orders —
a non-payment rate roughly 2× higher than credit card. &nbsp;
<strong>{top_inst["label"]}</strong> leads on high-installment exposure at {top_inst["high_inst_pct"]*100:.0f}% of orders in the 7x+ bucket,
where cancellation risk is measurably elevated.
</div>
""", unsafe_allow_html=True)

        st.divider()
        st.markdown("### Payment risk by state")
        st.markdown('<p class="kpi-label">Which regions lean hardest on boleto and high-installment credit</p>', unsafe_allow_html=True)

        if pay_by_state is not None:
            STATE_REGION = {
                "AC":"North","AM":"North","AP":"North","PA":"North","RO":"North","RR":"North","TO":"North",
                "AL":"Northeast","BA":"Northeast","CE":"Northeast","MA":"Northeast","PB":"Northeast",
                "PE":"Northeast","PI":"Northeast","RN":"Northeast","SE":"Northeast",
                "DF":"Center-West","GO":"Center-West","MS":"Center-West","MT":"Center-West",
                "ES":"Southeast","MG":"Southeast","RJ":"Southeast","SP":"Southeast",
                "PR":"South","RS":"South","SC":"South",
            }
            REGION_COLOR = {
                "North":"#38bdf8","Northeast":"#f5c542","Center-West":"#9b72cf",
                "Southeast":"#22d3a0","South":"#7c6bff",
            }
            pbs = pay_by_state.copy()
            pbs["region"] = pbs["state"].map(STATE_REGION).fillna("Other")
            pbs["region_color"] = pbs["region"].map(REGION_COLOR).fillna("#6060a0")
            pbs = pbs[pbs["total_orders"] >= 30].sort_values("boleto_pct", ascending=True)

            fig_state_pay = go.Figure()
            for region, grp in pbs.groupby("region", sort=False):
                color = REGION_COLOR.get(region, "#6060a0")
                fig_state_pay.add_trace(go.Bar(
                    name=region,
                    y=grp["state"],
                    x=grp["boleto_pct"] * 100,
                    orientation="h",
                    marker_color=color,
                    customdata=grp[["high_inst_pct", "total_orders", "avg_installments"]].values,
                    hovertemplate=(
                        "<b>%{y}</b><br>"
                        "Boleto: %{x:.1f}%<br>"
                        "High installments: %{customdata[0]:.1%}<br>"
                        "Avg installments: %{customdata[2]:.1f}x<br>"
                        "Orders: %{customdata[1]:,}<extra></extra>"
                    ),
                ))
            fig_state_pay.update_layout(**plot_layout(
                title="Boleto share by state (coloured by region)",
                height=560,
                barmode="overlay",
                xaxis=dict(title="% orders paid by boleto", ticksuffix="%"),
                yaxis=dict(title=""),
                legend=dict(orientation="h", y=1.06),
            ))
            st.plotly_chart(fig_state_pay, use_container_width=True)

            top_state = pbs.sort_values("boleto_pct", ascending=False).iloc[0]
            low_state = pbs.sort_values("boleto_pct", ascending=True).iloc[0]
            st.markdown(f"""
<div class="callout">
<strong>{top_state["state"]} ({STATE_REGION.get(top_state["state"], "")})</strong> has the highest boleto rate at {top_state["boleto_pct"]*100:.0f}% —
meaning nearly 1 in {int(round(1/top_state["boleto_pct"]))} orders in that state carries elevated settlement risk.
<strong>{low_state["state"]}</strong> is the least exposed at {low_state["boleto_pct"]*100:.0f}%.
Regional patterns track infrastructure and banking access: Northeast and North states skew higher on boleto; South and Southeast skew toward credit card.
</div>
""", unsafe_allow_html=True)
