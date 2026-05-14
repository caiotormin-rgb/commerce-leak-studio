import streamlit as st
import plotly.graph_objects as go

from shared import plot_layout, COLORS


def render(wf, cf, total_rev):
    st.markdown("### Sales overview")

    s_k1, s_k2, s_k3, s_k4 = st.columns(4)
    total_orders  = int(wf["shopify_orders"].sum())
    avg_aov       = total_rev / total_orders if total_orders else 0
    first_4 = wf.head(4)["shopify_revenue"].sum()
    last_4  = wf.tail(4)["shopify_revenue"].sum()
    recent_growth = (last_4 / first_4 - 1) * 100 if first_4 else 0
    top_category  = cf.groupby("category")["revenue"].sum().idxmax()

    s_k1.metric("Revenue",           f"R${total_rev/1e6:.1f}M")
    s_k2.metric("Orders",            f"{total_orders:,}")
    s_k3.metric("AOV",               f"R${avg_aov:.0f}")
    s_k4.metric("Recent vs Start",   f"{recent_growth:+.0f}%")

    col_s1, col_s2 = st.columns([3, 2])

    with col_s1:
        fig_sales = go.Figure()
        fig_sales.add_trace(go.Scatter(
            x=wf["week_start"], y=wf["shopify_revenue"],
            name="Revenue", mode="lines+markers",
            line=dict(color=COLORS["shopify"], width=2),
            marker=dict(size=3),
            fill="tozeroy",
            fillcolor="rgba(34,211,160,0.08)",
        ))
        fig_sales.add_trace(go.Bar(
            x=wf["week_start"], y=wf["shopify_orders"],
            name="Orders", marker_color="rgba(59,158,255,0.28)",
            yaxis="y2",
        ))
        fig_sales.update_layout(**plot_layout(
            title="Weekly Revenue and Orders",
            height=360,
            legend=dict(orientation="h", y=1.13),
            yaxis=dict(title="Revenue (BRL)", gridcolor="#1c1c2a"),
            yaxis2=dict(title="Orders", overlaying="y", side="right", showgrid=False),
        ))
        st.plotly_chart(fig_sales, use_container_width=True)

    with col_s2:
        category_sales = (
            cf.groupby("category", as_index=False)
            .agg(revenue=("revenue", "sum"))
            .sort_values("revenue", ascending=False)
            .head(7)
        )
        fig_mix = go.Figure(go.Pie(
            labels=category_sales["category"].str.replace("_", " ").str.title(),
            values=category_sales["revenue"],
            hole=0.55,
            marker=dict(colors=["#22d3a0", "#3b9eff", "#7c6bff", "#f5c542",
                                 "#9b72cf", "#38bdf8", "#ff8a4c"]),
        ))
        fig_mix.update_layout(**plot_layout(
            title="Revenue Mix by Category",
            height=360,
            showlegend=True,
            legend=dict(orientation="h", y=-0.05, font=dict(size=10)),
        ))
        st.plotly_chart(fig_mix, use_container_width=True)

    best_week = wf.loc[wf["shopify_revenue"].idxmax()]
    st.markdown(f"""
<div class="callout">
Peak week: <strong>{best_week['week_start'].strftime('%b %d, %Y')}</strong> —
<strong>R${best_week['shopify_revenue']:,.0f}</strong> revenue,
<strong>{int(best_week['shopify_orders']):,}</strong> orders.
Top category: <strong>{top_category.replace('_', ' ').title()}</strong>.
</div>
""", unsafe_allow_html=True)
