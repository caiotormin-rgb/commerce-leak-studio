from pathlib import Path
from datetime import datetime
from html import escape
import pandas as pd
import streamlit as st

CONSULTANCY_NAME = "Torm Data Co."
PRODUCT_NAME = "Margin Intelligence Report"
RETAILER_NAME = "Casa Viva"
RETAILER_CATEGORY = "Brazilian home, gifts, and lifestyle marketplace"
BRAND_PROMISE = "Real signals. No platform spin. Owner-ready actions."

PLOT_THEME = dict(
    paper_bgcolor="#09090e",
    plot_bgcolor="#09090e",
    font=dict(color="#8888aa", size=11, family="JetBrains Mono, monospace"),
    xaxis=dict(gridcolor="#1c1c2a", zerolinecolor="#1c1c2a"),
    yaxis=dict(gridcolor="#1c1c2a", zerolinecolor="#1c1c2a"),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#9090b0")),
    margin=dict(l=48, r=24, t=72, b=36),
)

COLORS = dict(
    shopify="#22d3a0",
    google="#3b9eff",
    meta="#ff6b6b",
    email="#f5c542",
    organic="#9b72cf",
    attribution="#7c6bff",
    fulfillment="#22d3a0",
    retention="#f5c542",
    claimed="#ff5566",
    geo="#38bdf8",
    returns="#ff8a4c",
)

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

DEMO_BRIEF = """WHAT HAPPENED: Google and Meta are claiming about 30% more revenue than Shopify actually recorded. The ad spend is working — but the dashboards are lying about how well. On top of that, enough deliveries are arriving late to visibly hurt customer ratings, and fewer than 1 in 50 buyers comes back for a second purchase.

WHAT IT MEANS: The leak isn’t in the ads. It’s in everything after the click. Late deliveries damage ratings. Poor ratings kill repeat purchases. And when customers don’t come back, every new order has to pay for itself from scratch. That’s why growing spend isn’t moving the bottom line.

FIRST ACTION: This week — switch from platform dashboards to total revenue ÷ total ad spend as the one number that guides spend decisions. Reach out to any customer whose order arrived more than three days late, before they leave a review. Assign someone to build a 45-day follow-up offer for first-time buyers, with a target of getting 1 in 20 to return."""


def plot_layout(**overrides):
    layout = PLOT_THEME.copy()
    for key, value in overrides.items():
        if isinstance(layout.get(key), dict) and isinstance(value, dict):
            merged = layout[key].copy()
            merged.update(value)
            layout[key] = merged
        else:
            layout[key] = value
    return layout


def brl(value):
    if value is None or pd.isna(value):
        return "—"
    value = float(value)
    if abs(value) >= 1_000_000:
        return f"R${value / 1_000_000:.1f}M"
    if abs(value) >= 1_000:
        return f"R${value / 1_000:.0f}k"
    return f"R${value:,.0f}"


def pct(value):
    if value is None or pd.isna(value):
        return "—"
    return f"{float(value):.1f}%"


def file_status(filename):
    p = Path("data") / filename
    if not p.exists():
        return "Missing"
    modified = datetime.fromtimestamp(p.stat().st_mtime).strftime("%b %d, %Y %H:%M")
    return f"Ready · {modified}"


def _safe_html(s):
    return escape(s).encode("ascii", "xmlcharrefreplace").decode("ascii")


def render_brief_box(text, opacity=1.0, intro=None):
    intro_html = f"<em>{_safe_html(intro)}</em>\n\n" if intro else ""
    return f'<div class="brief-box" style="opacity:{opacity}">{intro_html}{_safe_html(text)}</div>'


def generate_openai_brief(api_key, prompt_context, brief_placeholder):
    if not api_key:
        brief_placeholder.markdown(
            """
<div class="callout callout-red">
No API key provided. Enter your OpenAI API key in the sidebar, or use demo mode below.
</div>
""",
            unsafe_allow_html=True,
        )
        brief_placeholder.markdown(render_brief_box(DEMO_BRIEF), unsafe_allow_html=True)
        return

    with st.spinner("Generating brief..."):
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt_context}],
                max_tokens=600,
                stream=True,
            )
            brief_text = ""
            for chunk in stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta.content
                if delta:
                    brief_text += delta
                    brief_placeholder.markdown(
                        render_brief_box(f"{brief_text}▌"),
                        unsafe_allow_html=True,
                    )
            if brief_text:
                brief_placeholder.markdown(render_brief_box(brief_text), unsafe_allow_html=True)
            else:
                brief_placeholder.warning("The model returned an empty response. Try again.")
        except Exception as e:
            message = str(e)
            quota_like = any(t in message.lower() for t in ["quota", "rate limit", "insufficient_quota", "billing"])
            auth_like  = any(t in message.lower() for t in ["invalid_api_key", "incorrect api key", "401"])
            if auth_like:
                brief_placeholder.markdown("""
<div class="callout callout-red">
<strong>Invalid API key.</strong> Double-check the key in the sidebar — it should start with <code>sk-</code>. You can get a valid key at platform.openai.com/api-keys.
</div>
""", unsafe_allow_html=True)
            elif quota_like:
                brief_placeholder.markdown("""
<div class="callout callout-amber">
<strong>Quota exceeded.</strong> The OpenAI account is out of credits. Demo output shown below.
</div>
""", unsafe_allow_html=True)
                brief_placeholder.markdown(render_brief_box(DEMO_BRIEF, 0.78, "Demo output:"), unsafe_allow_html=True)
            else:
                brief_placeholder.markdown(f"""
<div class="callout callout-red">
<strong>Error:</strong> {escape(message)}
</div>
""", unsafe_allow_html=True)
