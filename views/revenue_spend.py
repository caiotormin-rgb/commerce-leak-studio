"""
Spend & Revenue — funnel chapter 1
Did the money in match the money out?
"""
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from shared import plot_layout, COLORS, brl, MONTH_NAMES


def render(wf, cf, total_rev, season_monthly, season_cat_monthly):
    wf = wf.copy()
    total_spend   = wf["total_spend"].sum()
    avg_mer       = total_rev / total_spend if total_spend else 0
    total_claimed = wf["total_claimed"].sum()
    overclaim_pct = (total_claimed / total_rev - 1) * 100 if total_rev else 0
    total_orders  = int(wf["shopify_orders"].sum())
    avg_aov       = total_rev / total_orders if total_orders else 0
    avg_ga4_miss  = wf["ga4_missing_pct"].mean()

    first_4 = wf.head(4)["shopify_revenue"].sum()
    last_4  = wf.tail(4)["shopify_revenue"].sum()
    growth  = (last_4 / first_4 - 1) * 100 if first_4 else 0

    wf["mer_baseline"] = wf["mer"].rolling(8, min_periods=3).mean()
    wf["mer_std"]      = wf["mer"].rolling(8, min_periods=3).std()
    wf["mer_lower"]    = wf["mer_baseline"] - 1.5 * wf["mer_std"]
    wf["mer_upper"]    = wf["mer_baseline"] + 1.5 * wf["mer_std"]
    wf["anomaly"]      = (wf["mer"] < wf["mer_lower"]) | (wf["mer"] > wf["mer_upper"])

    # ── Takeaway ─────────────────────────────────────────────────────────
    direction = "up" if growth >= 0 else "down"
    st.markdown(f"""
<div class="callout callout-green" style="font-size:14px;line-height:1.9">
<strong>The short version:</strong>&nbsp; Revenue is <strong>{direction} {abs(growth):.0f}%</strong> in the last 4 weeks
vs the 4 before. Ad platforms are collectively claiming
<strong>{overclaim_pct:.0f}% more than Shopify actually recorded.</strong>
Revenue per R$1 of ads ({avg_mer:.1f}x) is the only number that doesn't rely on platform self-reporting — use it as the spend guardrail.
</div>
""", unsafe_allow_html=True)

    # ── KPIs with hover explanations ─────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    k1.metric(
        "Total revenue", f"R${total_rev/1e6:.1f}M",
        help="Shopify-recorded gross revenue over the selected period — the ground truth, not platform estimates.",
    )
    k2.metric(
        "Orders", f"{total_orders:,}",
        help="Total orders placed in the selected period, per Shopify.",
    )
    k3.metric(
        "Revenue per R$1 of ads", f"{avg_mer:.2f}x",
        help="Total Shopify revenue ÷ total ad spend. Unlike platform-reported ROAS, this uses actual deposits. "
             "Analysts call this MER (Media Efficiency Ratio). Target 3x+ in a healthy margin environment.",
    )
    k4.metric(
        "Platforms overclaiming by", f"+{overclaim_pct:.0f}%",
        delta_color="inverse",
        help="How much more revenue Meta + Google claim vs what Shopify recorded. "
             "Platforms count the same conversion multiple times across channels — this is the gap.",
    )

    st.divider()

    # ── Q1: Are we growing? ───────────────────────────────────────────────
    st.markdown("### Are we growing?")

    top_category = cf.groupby("category")["revenue"].sum().idxmax()

    col_r1, col_r2 = st.columns([3, 2])
    with col_r1:
        fig_rev = go.Figure()
        fig_rev.add_trace(go.Scatter(
            x=wf["week_start"], y=wf["shopify_revenue"],
            name="Revenue", mode="lines+markers",
            line=dict(color=COLORS["shopify"], width=2),
            marker=dict(size=3),
            fill="tozeroy", fillcolor="rgba(34,211,160,0.08)",
        ))
        fig_rev.add_trace(go.Bar(
            x=wf["week_start"], y=wf["shopify_orders"],
            name="Orders", marker_color="rgba(59,158,255,0.28)", yaxis="y2",
        ))
        fig_rev.update_layout(**plot_layout(
            title="Weekly revenue and orders",
            height=340,
            legend=dict(orientation="h", y=1.13),
            yaxis=dict(title="Revenue (BRL)", gridcolor="#1c1c2a"),
            yaxis2=dict(title="Orders", overlaying="y", side="right", showgrid=False),
        ))
        st.plotly_chart(fig_rev, use_container_width=True)

    with col_r2:
        cat_rev = (
            cf.groupby("category", as_index=False)
            .agg(revenue=("revenue", "sum"))
            .sort_values("revenue", ascending=False)
            .head(7)
        )
        fig_mix = go.Figure(go.Pie(
            labels=cat_rev["category"].str.replace("_", " ").str.title(),
            values=cat_rev["revenue"],
            hole=0.55,
            marker=dict(colors=["#22d3a0", "#3b9eff", "#7c6bff", "#f5c542",
                                  "#9b72cf", "#38bdf8", "#ff8a4c"]),
        ))
        fig_mix.update_layout(**plot_layout(
            title="Revenue split by category",
            height=340,
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
Avg order value: <strong>R${avg_aov:.0f}</strong>.
Top category: <strong>{top_category.replace('_', ' ').title()}</strong>.
</div>
""", unsafe_allow_html=True)

    st.divider()

    # ── Q2: Are our ad platforms reporting accurately? ────────────────────
    st.markdown("### Are our ad platforms reporting what actually happened?")
    st.markdown(
        '<p style="color:#8d8daf;font-size:14px;margin:-8px 0 20px">'
        "Each platform claims the same customer as its own win. "
        "Add them up and you get more than 100% of actual revenue — one sale, three winners."
        "</p>",
        unsafe_allow_html=True,
    )

    col_a1, col_a2 = st.columns([3, 2])
    with col_a1:
        fig_claim = go.Figure()
        fig_claim.add_trace(go.Bar(
            x=wf["week_start"], y=wf["shopify_revenue"],
            name="Shopify (actual)", marker_color=COLORS["shopify"], opacity=0.9,
        ))
        fig_claim.add_trace(go.Scatter(
            x=wf["week_start"], y=wf["total_claimed"],
            name="Platforms' combined claim", mode="lines",
            line=dict(color=COLORS["claimed"], width=2, dash="dot"),
        ))
        fig_claim.update_layout(**plot_layout(
            title="What Shopify recorded vs what platforms claim",
            barmode="overlay", height=320,
            legend=dict(orientation="h", y=1.15),
        ))
        st.plotly_chart(fig_claim, use_container_width=True)

    with col_a2:
        fig_mer = go.Figure()
        fig_mer.add_trace(go.Scatter(
            x=pd.concat([wf["week_start"], wf["week_start"][::-1]]),
            y=pd.concat([wf["mer_upper"], wf["mer_lower"][::-1]]),
            fill="toself", fillcolor="rgba(124,107,255,0.07)",
            line=dict(color="rgba(0,0,0,0)"), name="Normal range",
        ))
        fig_mer.add_trace(go.Scatter(
            x=wf["week_start"], y=wf["mer_baseline"],
            name="8-week average", line=dict(color="#444466", width=1.5, dash="dot"),
        ))
        fig_mer.add_trace(go.Scatter(
            x=wf["week_start"], y=wf["mer"],
            name="Revenue per R$1 of ads", mode="lines+markers",
            line=dict(color=COLORS["attribution"], width=2),
            marker=dict(size=3),
        ))
        anoms = wf[wf["anomaly"] & wf["mer_baseline"].notna()]
        if len(anoms):
            fig_mer.add_trace(go.Scatter(
                x=anoms["week_start"], y=anoms["mer"],
                name="Unusual week", mode="markers",
                marker=dict(color="#ff5566", size=9, symbol="circle-open",
                            line=dict(width=2)),
            ))
        fig_mer.update_layout(**plot_layout(
            title="Revenue per R$1 of ads — weekly trend",
            height=320, legend=dict(orientation="h", y=1.12),
            yaxis=dict(title="Revenue / Spend"),
        ))
        st.plotly_chart(fig_mer, use_container_width=True)

    # ── Channel detail (expander) ─────────────────────────────────────────
    with st.expander("Channel breakdown & tracking gaps", expanded=False):
        avg_google_rep  = (wf["google_reported_revenue"] / wf["google_spend"]).mean()
        avg_meta_rep    = (wf["meta_reported_revenue"]   / wf["meta_spend"]).mean()
        avg_google_true = (wf["google_true"] / wf["google_spend"]).mean()
        avg_meta_true   = (wf["meta_true"]   / wf["meta_spend"]).mean()
        avg_shopify_wk  = wf["shopify_revenue"].mean()
        avg_claimed_wk  = wf["total_claimed"].mean()
        phantom_total   = wf["total_claimed"].sum() - wf["shopify_revenue"].sum()

        ch1, ch2, ch3 = st.columns(3)
        with ch1:
            st.markdown(f"""
<div style="background:#0f0f18;border:1px solid #1c1c2a;border-radius:10px;padding:16px">
<p class="kpi-label">Google Ads</p>
<p style="font-size:24px;font-weight:800;color:#3b9eff;margin:4px 0">
  {avg_google_rep:.1f}x <span style="font-size:13px;color:#444466">claimed</span>
</p>
<p style="font-size:18px;font-weight:600;color:#22d3a0">
  {avg_google_true:.1f}x <span style="font-size:12px;color:#444466">actual</span>
</p>
<p style="font-size:11px;color:#5a5a78;margin-top:6px">
  ~{(avg_google_rep/avg_google_true - 1)*100:.0f}% overclaim — PMax + cross-channel double-counting
</p>
</div>
""", unsafe_allow_html=True)
        with ch2:
            st.markdown(f"""
<div style="background:#0f0f18;border:1px solid #1c1c2a;border-radius:10px;padding:16px">
<p class="kpi-label">Meta Ads</p>
<p style="font-size:24px;font-weight:800;color:#ff6b6b;margin:4px 0">
  {avg_meta_rep:.1f}x <span style="font-size:13px;color:#444466">claimed</span>
</p>
<p style="font-size:18px;font-weight:600;color:#22d3a0">
  {avg_meta_true:.1f}x <span style="font-size:12px;color:#444466">actual</span>
</p>
<p style="font-size:11px;color:#5a5a78;margin-top:6px">
  ~{(avg_meta_rep/avg_meta_true - 1)*100:.0f}% overclaim — 7-day click / 1-day view window
</p>
</div>
""", unsafe_allow_html=True)
        with ch3:
            st.markdown(f"""
<div style="background:#200a10;border:1px solid #ff556630;border-radius:10px;padding:16px">
<p class="kpi-label" style="color:#ff5566">Combined overclaim</p>
<p style="font-size:24px;font-weight:800;color:#ff5566;margin:4px 0">+{overclaim_pct:.0f}%</p>
<p style="font-size:13px;color:#d0a0a8">R${avg_claimed_wk:,.0f} claimed vs R${avg_shopify_wk:,.0f} actual per week</p>
<p style="font-size:11px;color:#804040;margin-top:6px">R${phantom_total:,.0f} in phantom revenue over this period</p>
</div>
""", unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        col_sp1, col_sp2 = st.columns(2)
        with col_sp1:
            fig_spend = go.Figure()
            for ch, color, name in [
                ("google_spend", COLORS["google"], "Google"),
                ("meta_spend",   COLORS["meta"],   "Meta"),
                ("email_cost",   COLORS["email"],  "Email"),
            ]:
                fig_spend.add_trace(go.Bar(
                    x=wf["week_start"], y=wf[ch],
                    name=name, marker_color=color, opacity=0.8,
                ))
            fig_spend.update_layout(**plot_layout(
                barmode="stack", title="Ad spend by channel",
                height=280, legend=dict(orientation="h", y=1.15),
                yaxis=dict(title="BRL"),
            ))
            st.plotly_chart(fig_spend, use_container_width=True)

        with col_sp2:
            fig_ga4 = go.Figure()
            fig_ga4.add_trace(go.Scatter(
                x=wf["week_start"], y=wf["shopify_revenue"],
                name="Shopify", fill="tozeroy",
                line=dict(color=COLORS["shopify"], width=2),
                fillcolor="rgba(34,211,160,0.08)",
            ))
            fig_ga4.add_trace(go.Scatter(
                x=wf["week_start"], y=wf["ga4_revenue"],
                name="GA4", fill="tozeroy",
                line=dict(color="#888899", width=1.5, dash="dash"),
                fillcolor="rgba(136,136,153,0.06)",
            ))
            fig_ga4.update_layout(**plot_layout(
                title=f"Analytics tracking gap — GA4 misses {avg_ga4_miss:.0f}% of revenue",
                height=280, legend=dict(orientation="h", y=1.15),
            ))
            st.plotly_chart(fig_ga4, use_container_width=True)

        st.markdown("""
<div class="callout">
<strong>Why GA4 misses revenue:</strong> ad blockers (25–35% of desktop), iOS Safari 7-day cookie limit,
payment redirects killing the checkout event, and Shopify's new checkout restricting GTM.
<strong>Fix:</strong> server-side tracking via GTM Server Container + Meta CAPI + Google Enhanced Conversions.
</div>
""", unsafe_allow_html=True)

    # ── Seasonality (expander) ────────────────────────────────────────────
    if season_monthly is not None:
        with st.expander("When do we sell the most? — seasonal patterns", expanded=False):
            sm = season_monthly.copy()
            sm["month_name"] = sm["month_num"].apply(lambda m: MONTH_NAMES[m - 1])
            sm = sm.sort_values("purchase_month").reset_index(drop=True)

            peak_row   = sm.loc[sm["orders"].idxmax()]
            trough_row = sm.loc[sm["orders"].idxmin()]
            peak_ratio = peak_row["orders"] / trough_row["orders"]

            y17 = sm[sm["year"] == 2017].set_index("month_num")["orders"]
            y18 = sm[sm["year"] == 2018].set_index("month_num")["orders"]
            shared = y17.index.intersection(y18.index)
            yoy = (y18[shared].sum() / y17[shared].sum() - 1) * 100 if len(shared) else 0

            ds1, ds2, ds3 = st.columns(3)
            ds1.metric(
                "Peak month", peak_row["purchase_month"],
                f"{int(peak_row['orders']):,} orders",
                help="The busiest month historically. Use this to time inventory buys and ad spend increases.",
            )
            ds2.metric(
                "Quietest month", trough_row["purchase_month"],
                f"{int(trough_row['orders']):,} orders",
                help="The slowest month historically — good for clearance, reduced spend, or maintenance windows.",
            )
            ds3.metric(
                "Peak vs quiet", f"{peak_ratio:.1f}×",
                help="How much busier the peak month is vs the slowest. Higher = more seasonal, needs more pre-stocking.",
            )

            col_d1, col_d2 = st.columns(2)
            with col_d1:
                month_avg   = sm.groupby("month_num")["orders"].mean()
                overall_avg = sm["orders"].mean()
                idx = (month_avg / overall_avg * 100).reset_index()
                idx.columns = ["month_num", "index"]
                idx["month_name"] = idx["month_num"].apply(lambda m: MONTH_NAMES[m - 1])
                idx["color"] = idx["index"].apply(lambda v: "#f5c542" if v >= 100 else "#3b9eff")

                fig_idx = go.Figure(go.Bar(
                    x=idx["month_name"], y=idx["index"],
                    marker_color=idx["color"],
                    text=idx["index"].map(lambda v: f"{v:.0f}"),
                    textposition="outside",
                    hovertemplate="%{x}<br>%{y:.0f} vs average month<extra></extra>",
                ))
                fig_idx.add_hline(y=100, line_dash="dot", line_color="#2a2a40",
                                  annotation_text="average",
                                  annotation_font_color="#5a5a78",
                                  annotation_position="right")
                fig_idx.update_layout(**plot_layout(
                    title="Which months run above / below average  (100 = average month)",
                    height=280,
                    yaxis=dict(title="Index", range=[50, 165]),
                    xaxis=dict(title=""),
                ))
                st.plotly_chart(fig_idx, use_container_width=True)

            with col_d2:
                YEAR_COLORS = {2016: "#9b72cf", 2017: "#3b9eff", 2018: "#22d3a0"}
                fig_yoy = go.Figure()
                for yr, grp in sm.groupby("year"):
                    grp = grp.sort_values("month_num")
                    fig_yoy.add_trace(go.Scatter(
                        x=grp["month_name"], y=grp["orders"],
                        name=str(yr), mode="lines+markers",
                        line=dict(color=YEAR_COLORS.get(yr, "#888899"), width=2),
                        marker=dict(size=5),
                        opacity=0.5 if yr == 2016 else 1.0,
                    ))
                fig_yoy.update_layout(**plot_layout(
                    title=f"Year-over-year — {yoy:+.0f}% growth on shared months",
                    height=280,
                    xaxis=dict(title="Month", categoryorder="array",
                               categoryarray=MONTH_NAMES),
                    yaxis=dict(title="Orders"),
                    legend=dict(orientation="h", y=1.15),
                ))
                st.plotly_chart(fig_yoy, use_container_width=True)
