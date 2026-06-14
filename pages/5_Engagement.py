"""Engagement page — Q5 engagement vs grade · Q10 age band (split into 3 panels).

v3: Q10 is now three single-metric charts side-by-side so the 'age barely
moves the needle' story is visible at a glance — each panel carries its own
appropriate y-axis scale and a dashed platform-mean reference line.
"""
import streamlit as st

from config import APP_NAME, FAVICON_PATH
from auth import require_auth
from components.injector import inject_styles
from components.cards import render_page_header
from components.sidebar import (
    render_sidebar, apply_master_filters, render_active_filter_chips,
)
from components.charts import (
    chart_q9_attendance_trend,
   
    chart_q5a_engagement_grade,
    chart_q5b_engagement_activity,
    chart_q10_age_grade,
    chart_q10_age_attendance,
    chart_q10_age_engagement,
)
from components.observations import render_insight_cta
from utils.queries import master, monthly_attendance


st.set_page_config(page_title=f"Engagement · {APP_NAME}", page_icon=str(FAVICON_PATH),
                   layout="wide", initial_sidebar_state="expanded")
inject_styles()
require_auth()
filters = render_sidebar(active="engagement")

render_page_header(
    "Engagement",
    "Platform behavior and demographics — how login activity and age relate to outcomes.",
)
render_active_filter_chips(filters)

df = master()
df = apply_master_filters(df, filters)

# --- Q9 (relocated from Overview — March 2026 cohort dip belongs here) ---
st.markdown(
    '<div class="kf-section-h">Q9 · Cohort Trend Over 6 Months</div>'
    '<div class="kf-section-sub">Monthly attendance and platform activity across the entire term. '
    'Trends are platform-wide and unaffected by sidebar filters.</div>',
    unsafe_allow_html=True,
)

mdf = monthly_attendance()
if not mdf.empty:
    st.plotly_chart(chart_q9_attendance_trend(mdf), use_container_width=True)

render_insight_cta(
    insight=(
        "<strong>March 2026</strong> is the only month showing a clear institution-wide "
        "engagement disruption. Student behavior before and after March is consistent, "
        "suggesting the decline was caused by a temporary external factor rather than a "
        "long-term learning problem."
    ),
    cta=(
        "<strong>Investigate March 2026:</strong> midterm schedules, assignment deadlines, "
        "public holidays, LMS incidents, instructor absenteeism, or academic-calendar "
        "changes. Stand up an early-warning system that fires when attendance falls more "
        "than 10 percentage points below the rolling average — March would have been "
        "flagged immediately. If March aligns with assessment periods, spread large "
        "assessments across multiple weeks instead of concentrating them into a single month."
    ),
)

# --- Q5 ---
st.markdown('<div class="kf-section-h">Q5 · Engagement vs Academic Performance</div>'
            '<div class="kf-section-sub">Login frequency and platform activity, by engagement quartile.</div>',
            unsafe_allow_html=True)

if df is not None and not df.empty:
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(chart_q5a_engagement_grade(df), use_container_width=True)
    with c2:
        st.plotly_chart(chart_q5b_engagement_activity(df), use_container_width=True)
else:
    st.info("No students match the current filters.")

render_insight_cta(
    insight=(
        "Students with high platform engagement (~80 activities) achieve a "
        "<strong>74.5%</strong> average grade, compared to <strong>66.7%</strong> for "
        "low-engagement students (~44 activities). Active learning behaviour is strongly "
        "associated with academic performance."
    ),
    cta=(
        "Use platform engagement as an early-warning metric. Trigger intervention when "
        "student activity falls below <strong>50 interactions</strong> — low engagement is "
        "associated with significantly lower academic achievement."
    ),
)

# --- Q10 (3-panel rework) ---
st.markdown('<div class="kf-section-h">Q10 · Outcomes by Age Band</div>'
            '<div class="kf-section-sub">Three separate metrics across the same age bands. '
            'The dashed line on each panel is the platform mean — bars close to it mean '
            "age doesn't materially change that outcome.</div>",
            unsafe_allow_html=True)

if df is not None and not df.empty:
    a1, a2, a3 = st.columns(3)
    with a1:
        st.plotly_chart(chart_q10_age_grade(df), use_container_width=True)
    with a2:
        st.plotly_chart(chart_q10_age_attendance(df), use_container_width=True)
    with a3:
        st.plotly_chart(chart_q10_age_engagement(df), use_container_width=True)

render_insight_cta(
    insight=(
        "Grade and engagement are essentially flat across every age band — the bars "
        "sit on the mean line in both panels. The only visible difference is "
        "<strong>attendance</strong>, where the 30+ cohort dips below the platform "
        "average. Once attendance is held constant, age explains very little of the "
        "variance in outcomes — meaning the 30+ group's apparent weakness is an "
        "<strong>attendance pattern</strong>, not an age effect."
    ),
    cta=(
        "Focus retention and support efforts for the 30+ cohort on the operational "
        "side — flexible scheduling, attendance scaffolding, and proactive "
        "outreach — rather than on academic content. The data does not support "
        "treating older learners as academically weaker; it supports treating them "
        "as <strong>less consistent attenders</strong>."
    ),
)
