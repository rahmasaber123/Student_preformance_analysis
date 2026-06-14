"""Insight + Recommended-Action cards — matches the brand layout from the screenshot.

Usage:
    render_insight_cta("The platform-wide attendance rate is 75.8%...",
                       "Prioritise Group 07. Review the instructor...")
"""
import streamlit as st


def render_insight(text: str) -> None:
    """White card with left-blue accent border + 'INSIGHT' label."""
    html = f"""
    <div class="kf-card kf-insight">
      <div class="kf-card-label">INSIGHT</div>
      <div class="kf-card-body">{text}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_cta(text: str) -> None:
    """Light lavender card with 'RECOMMENDED ACTION' label."""
    html = f"""
    <div class="kf-card kf-cta">
      <div class="kf-card-label">RECOMMENDED ACTION</div>
      <div class="kf-card-body">{text}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_insight_cta(insight: str, cta: str) -> None:
    """Render both cards stacked vertically — the standard layout."""
    render_insight(insight)
    render_cta(cta)
