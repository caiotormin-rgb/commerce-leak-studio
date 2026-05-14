import streamlit as st
import plotly.graph_objects as go

from shared import plot_layout, COLORS


def render(wf):
    st.markdown(
        '<p style="color:#7c6bff;font-size:10px;letter-spacing:.15em;'
        'text-transform:uppercase;font-family:monospace;margin:0 0 4px">Attribution</p>',
        unsafe_allow_html=True,
    )
    st.markdown("### What platforms claim vs what actually happened")

    st.markdown("""
<div class="callout callout-red">
<strong>The impossible math:</strong> Meta, Google, and Email each claim the same customer journey.
Sum their reported revenue and you get <strong>~140% of actual Shopify revenue</strong>.
One sale. Three winners.
</div>
""", unsafe_allow_html=True)

    fig_lie = go.Figure()
    fig_lie.add_trace(go.Bar(
        x=wf["week_start"], y=wf["shopify_revenue"],
        name="Shopify (truth)", marker_color=COLORS["shopify"], opacity=0.9,
    ))
    fig_lie.add_trace(go.Scatter(
        x=wf["week_start"], y=wf["total_claimed"],
        name="Total claimed by platforms", mode="lines",
        line=dict(color=COLORS["claimed"], width=2, dash="dot"),
    ))
    fig_lie.update_layout(**plot_layout(
        title="Weekly Revenue: Shopify Truth vs Platform Claims",
        barmode="overlay", height=320,
        legend=dict(orientation="h", y=1.15),
    ))
    st.plotly_chart(fig_lie, use_container_width=True)

    st.markdown("#### Platform ROAS: Reported vs True")
    col_a, col_b, col_c = st.columns(3)

    avg_google_rep  = (wf["google_reported_revenue"] / wf["google_spend"]).mean()
    avg_meta_rep    = (wf["meta_reported_revenue"]   / wf["meta_spend"]).mean()
    avg_google_true = (wf["google_true"] / wf["google_spend"]).mean()
    avg_meta_true   = (wf["meta_true"]   / wf["meta_spend"]).mean()

    with col_a:
        st.markdown("""
<div style="background:#0f0f18;border:1px solid #1c1c2a;border-radius:10px;padding:16px">
<p class="kpi-label">Google Ads</p>
<p style="font-size:28px;font-weight:800;color:#3b9eff;margin:4px 0">
  {:.1f}x <span style="font-size:14px;color:#444466">reported</span>
</p>
<p style="font-size:22px;font-weight:600;color:#22d3a0">
  {:.1f}x <span style="font-size:12px;color:#444466">true</span>
</p>
<p style="font-size:11px;color:#5a5a78;margin-top:6px">
  ~{:.0f}% overclaim — PMax + DDA cross-channel double-counting
</p>
</div>
""".format(avg_google_rep, avg_google_true, (avg_google_rep/avg_google_true - 1)*100),
        unsafe_allow_html=True)

    with col_b:
        st.markdown("""
<div style="background:#0f0f18;border:1px solid #1c1c2a;border-radius:10px;padding:16px">
<p class="kpi-label">Meta Ads</p>
<p style="font-size:28px;font-weight:800;color:#ff6b6b;margin:4px 0">
  {:.1f}x <span style="font-size:14px;color:#444466">reported</span>
</p>
<p style="font-size:22px;font-weight:600;color:#22d3a0">
  {:.1f}x <span style="font-size:12px;color:#444466">true</span>
</p>
<p style="font-size:11px;color:#5a5a78;margin-top:6px">
  ~{:.0f}% overclaim — 7-day click / 1-day view + Advantage+ opacity
</p>
</div>
""".format(avg_meta_rep, avg_meta_true, (avg_meta_rep/avg_meta_true - 1)*100),
        unsafe_allow_html=True)

    with col_c:
        avg_claimed_weekly = wf["total_claimed"].mean()
        avg_shopify_weekly = wf["shopify_revenue"].mean()
        avg_overclaim      = wf["overclaim_pct"].mean()
        st.markdown("""
<div style="background:#200a10;border:1px solid #ff556630;border-radius:10px;padding:16px">
<p class="kpi-label" style="color:#ff5566">Combined Overclaim</p>
<p style="font-size:28px;font-weight:800;color:#ff5566;margin:4px 0">
  +{:.0f}%
</p>
<p style="font-size:13px;color:#d0a0a8">
  R${:,.0f} claimed vs R${:,.0f} actual per week
</p>
<p style="font-size:11px;color:#804040;margin-top:6px">
  R${:,.0f} in phantom revenue over this period
</p>
</div>
""".format(avg_overclaim, avg_claimed_weekly, avg_shopify_weekly,
           wf["total_claimed"].sum() - wf["shopify_revenue"].sum()),
        unsafe_allow_html=True)

    st.markdown('<div class="pillar-section"></div>', unsafe_allow_html=True)
    st.markdown("### Revenue per R$1 of ad spend — the one number that doesn't lie")
    st.markdown("""
<div class="callout" style="border-left-color:#7c6bff">
<strong>Media Efficiency Ratio</strong> = Total Shopify Revenue ÷ Total Ad Spend.
No attribution models, no platform self-reporting. Track this weekly and watch it move
as you change channel mix.
</div>
""", unsafe_allow_html=True)

    wf = wf.copy()
    wf["mer_baseline"] = wf["mer"].rolling(8, min_periods=4).mean()
    wf["mer_std"]      = wf["mer"].rolling(8, min_periods=4).std()
    wf["mer_upper"]    = wf["mer_baseline"] + 1.5 * wf["mer_std"]
    wf["mer_lower"]    = wf["mer_baseline"] - 1.5 * wf["mer_std"]
    wf["anomaly"]      = (wf["mer"] < wf["mer_lower"]) | (wf["mer"] > wf["mer_upper"])

    col_m1, col_m2 = st.columns([3, 2])

    with col_m1:
        import pandas as pd
        fig_mer = go.Figure()
        fig_mer.add_trace(go.Scatter(
            x=pd.concat([wf["week_start"], wf["week_start"][::-1]]),
            y=pd.concat([wf["mer_upper"], wf["mer_lower"][::-1]]),
            fill="toself", fillcolor="rgba(124,107,255,0.07)",
            line=dict(color="rgba(0,0,0,0)"),
            name="Normal range",
        ))
        fig_mer.add_trace(go.Scatter(
            x=wf["week_start"], y=wf["mer_baseline"],
            name="8-wk baseline", line=dict(color="#444466", width=1.5, dash="dot"),
        ))
        fig_mer.add_trace(go.Scatter(
            x=wf["week_start"], y=wf["mer"],
            name="MER", mode="lines+markers",
            line=dict(color=COLORS["attribution"], width=2),
            marker=dict(size=3),
        ))
        anoms = wf[wf["anomaly"] & wf["mer_baseline"].notna()]
        if len(anoms):
            fig_mer.add_trace(go.Scatter(
                x=anoms["week_start"], y=anoms["mer"],
                name="Anomaly", mode="markers",
                marker=dict(color="#ff5566", size=9, symbol="circle-open",
                            line=dict(width=2)),
            ))
        for _, row in wf[wf["season_label"] != ""].iterrows():
            fig_mer.add_annotation(
                x=row["week_start"], y=row["mer"] + 0.05,
                text=row["season_label"], showarrow=False,
                font=dict(size=8, color="#666699"), bgcolor="rgba(0,0,0,0.3)",
            )
        fig_mer.update_layout(**plot_layout(
            title="Weekly MER with Anomaly Detection",
            height=340, legend=dict(orientation="h", y=1.12),
            yaxis=dict(title="MER (Revenue / Spend)"),
        ))
        st.plotly_chart(fig_mer, use_container_width=True)

    with col_m2:
        fig_spend = go.Figure()
        for ch, col_name, name in [
            ("google_spend", COLORS["google"], "Google"),
            ("meta_spend",   COLORS["meta"],   "Meta"),
            ("email_cost",   COLORS["email"],  "Email"),
        ]:
            fig_spend.add_trace(go.Bar(
                x=wf["week_start"], y=wf[ch],
                name=name, marker_color=col_name, opacity=0.8,
            ))
        fig_spend.update_layout(**plot_layout(
            barmode="stack",
            title="Spend Mix by Channel",
            height=340, legend=dict(orientation="h", y=1.15),
            yaxis=dict(title="BRL"),
        ))
        st.plotly_chart(fig_spend, use_container_width=True)

    st.markdown('<div class="pillar-section"></div>', unsafe_allow_html=True)
    st.markdown("### The GA4 gap — why analytics don't match your bank account")

    col_ga1, col_ga2 = st.columns([3, 2])

    with col_ga1:
        fig_ga4 = go.Figure()
        fig_ga4.add_trace(go.Scatter(
            x=wf["week_start"], y=wf["shopify_revenue"],
            name="Shopify (truth)", fill="tozeroy",
            line=dict(color=COLORS["shopify"], width=2),
            fillcolor="rgba(34,211,160,0.08)",
        ))
        fig_ga4.add_trace(go.Scatter(
            x=wf["week_start"], y=wf["ga4_revenue"],
            name="GA4 (broken client-side)", fill="tozeroy",
            line=dict(color="#888899", width=1.5, dash="dash"),
            fillcolor="rgba(136,136,153,0.06)",
        ))
        fig_ga4.update_layout(**plot_layout(
            title="Shopify Revenue vs GA4 Tracked Revenue",
            height=280, legend=dict(orientation="h", y=1.15),
        ))
        st.plotly_chart(fig_ga4, use_container_width=True)

    with col_ga2:
        st.markdown("""
<div class="callout" style="margin-top:32px">
<strong>Why the gap exists:</strong><br><br>
🔹 <strong>Ad blockers</strong>: 25–35% of desktop users block GA4<br><br>
🔹 <strong>iOS ITP</strong>: Safari caps first-party cookies at 7 days<br><br>
🔹 <strong>Payment redirects</strong>: Stripe/PayPal kills the thank_you event<br><br>
🔹 <strong>Shopify Checkout</strong>: GTM restricted in new checkout<br><br>
<strong>Fix:</strong> Server-side tracking via GTM Server Container + Meta CAPI
+ Google Enhanced Conversions
</div>
""", unsafe_allow_html=True)
