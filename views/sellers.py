import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from shared import plot_layout, COLORS


def render(seller_perf, seller_conc):
    st.markdown("### Seller performance & revenue concentration")
    st.markdown(
        '<p class="kpi-label">Real Olist dataset · 1,238 qualifying sellers · 10+ orders each</p>',
        unsafe_allow_html=True,
    )

    if seller_perf is None:
        st.warning("Run `python scripts/build_olist_data.py` first.", icon="⚙️")
    else:
        total_rev_s = seller_perf["revenue"].sum()
        top10_share = seller_perf.head(10)["revenue"].sum() / total_rev_s * 100
        avg_score_s = np.average(seller_perf["avg_review_score"], weights=seller_perf["orders"])
        sp_share    = (seller_perf[seller_perf["seller_state"] == "SP"]["orders"].sum()
                       / seller_perf["orders"].sum() * 100)

        sk1, sk2, sk3, sk4 = st.columns(4)
        sk1.metric("Qualifying Sellers",   f"{len(seller_perf):,}")
        sk2.metric("Top 10 Revenue Share", f"{top10_share:.1f}%")
        sk3.metric("Avg Review Score",     f"{avg_score_s:.2f}★")
        sk4.metric("SP Seller Share",      f"{sp_share:.0f}% of orders")

        st.divider()
        col_s1, col_s2 = st.columns([3, 2])

        with col_s1:
            fig_scatter_s = px.scatter(
                seller_perf.head(200),
                x="revenue", y="avg_review_score",
                size="orders", color="on_time_rate",
                color_continuous_scale="RdYlGn",
                hover_name="seller_id",
                hover_data={
                    "seller_state": True,
                    "top_category": True,
                    "orders": ":,",
                    "revenue": ":,.0f",
                    "on_time_rate": ":.1%",
                    "avg_review_score": ":.2f",
                },
                labels={
                    "revenue": "Revenue (BRL)",
                    "avg_review_score": "Avg review score",
                    "on_time_rate": "On-time",
                },
                size_max=30,
            )
            fig_scatter_s.update_layout(**plot_layout(
                title="Revenue vs Review Score  (top 200 sellers · colour = on-time rate)",
                height=420,
                coloraxis_colorbar=dict(title="On-time", tickformat=".0%", thickness=10),
            ))
            st.plotly_chart(fig_scatter_s, use_container_width=True)

        with col_s2:
            fig_pareto = go.Figure(go.Scatter(
                x=list(range(1, len(seller_conc) + 1)),
                y=seller_conc["cumulative_revenue_pct"],
                mode="lines",
                fill="tozeroy",
                fillcolor="rgba(124,107,255,0.15)",
                line=dict(color=COLORS["attribution"], width=2),
                hovertemplate="Top %{x} sellers<br>%{y:.1f}% of revenue<extra></extra>",
            ))
            fig_pareto.add_hline(y=80, line_dash="dot",
                line_color="#f5c542", annotation_text="80%",
                annotation_position="right")
            fig_pareto.update_layout(**plot_layout(
                title="How many sellers drive 80% of revenue",
                height=420,
                xaxis=dict(title="Seller rank"),
                yaxis=dict(title="Cumulative revenue %", range=[0, 101]),
            ))
            st.plotly_chart(fig_pareto, use_container_width=True)

        with st.expander("Worst-rated sellers (min 50 orders)"):
            worst_sellers = (
                seller_perf[seller_perf["orders"] >= 50]
                .nsmallest(12, "avg_review_score")
                [["seller_id", "seller_state", "top_category", "orders",
                  "revenue", "on_time_rate", "avg_review_score"]]
                .copy()
            )
            worst_sellers["revenue"]          = worst_sellers["revenue"].map(lambda v: f"R${v:,.0f}")
            worst_sellers["on_time_rate"]     = worst_sellers["on_time_rate"].map(lambda v: f"{v*100:.1f}%")
            worst_sellers["avg_review_score"] = worst_sellers["avg_review_score"].map(lambda v: f"{v:.2f}★")
            worst_sellers["seller_id"]        = worst_sellers["seller_id"].str[:12] + "…"
            st.dataframe(worst_sellers, use_container_width=True, hide_index=True)
