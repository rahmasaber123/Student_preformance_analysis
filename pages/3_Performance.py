"""Performance page — Q3 by course · Instructor cut · Q2 by type · Q4 attendance · Q8 lateness.

v3: adds the "Average Student Grade by Instructor" chart from the Q3 deep-dive.
"""
import streamlit as st

from config import APP_NAME, FAVICON_PATH
from auth import require_auth
from components.injector import inject_styles
from components.cards import render_page_header
from components.sidebar import (
    render_sidebar, apply_master_filters, filter_by_course,
    render_active_filter_chips,
)
from components.charts import (
    chart_q3_course_grade,
    chart_instructor_grade,
    chart_hossam_pie,
    chart_q2_type_stats,
    chart_q4_attendance_band,
    chart_q8_late_vs_ontime,
)
from components.observations import render_insight_cta
from utils.queries import course_stats, type_stats, master, late_submission_impact


st.set_page_config(page_title=f"Performance · {APP_NAME}", page_icon=str(FAVICON_PATH),
                   layout="wide", initial_sidebar_state="expanded")
inject_styles()
require_auth()
filters = render_sidebar(active="performance")

render_page_header(
    "Performance",
    "Where the platform scores well, where it doesn't, and what drives the gap.",
)
render_active_filter_chips(filters)

# Master is used by several charts on this page; fetch once.
master_df = master()
master_filtered = apply_master_filters(master_df, filters)

# --- Q3 ---
st.markdown('<div class="kf-section-h">Q3 · Average Grade by Course</div>'
            '<div class="kf-section-sub">Which course leads, which lags?</div>',
            unsafe_allow_html=True)

df = course_stats()
df = filter_by_course(df, filters, "course_id")
if not df.empty:
    st.plotly_chart(chart_q3_course_grade(df), use_container_width=True)
else:
    st.info("No courses match the current filters.")

render_insight_cta(
    insight=(
        "<strong>Digital Marketing</strong> has the lowest average grade among all courses "
        "(<strong>59.1%</strong>), significantly below the platform average. This is "
        "consistent with previous findings: the course also has the lowest attendance, "
        "weakest assignment performance, lowest concept mastery, and highest late-submission "
        "rate. The repeated appearance of Digital Marketing across risk indicators points "
        "to a systemic course-level issue."
    ),
    cta=(
        "Conduct a detailed review of the Digital Marketing course: assignment design, "
        "assessment difficulty, student support, and engagement strategies. Re-evaluate "
        "instructor-course alignment. Since the course underperforms across multiple metrics, "
        "improvements here will produce the greatest impact on overall outcomes."
    ),
)

# --- Q3 deep-dive: Instructor cut ---
st.markdown('<div class="kf-section-h">Q3 · Average Student Grade by Instructor</div>'
            '<div class="kf-section-sub">Same data, sliced by instructor — is the course a teaching problem or a content problem?</div>',
            unsafe_allow_html=True)

if master_filtered is not None and not master_filtered.empty:
    ic1, ic2 = st.columns([3, 2])
    with ic1:
        st.plotly_chart(chart_instructor_grade(master_filtered), use_container_width=True)
    with ic2:
        st.plotly_chart(chart_hossam_pie(master_filtered), use_container_width=True)
else:
    st.info("No instructor data matches the current filters.")

render_insight_cta(
    insight=(
        "<strong>Eng. Hossam Refaat's</strong> performance varies substantially across his courses. "
        "His Python Programming group performs near the platform average, while his "
        "Digital Marketing group records the lowest performance across multiple metrics. "
        "This pattern suggests the issue is the <strong>course itself</strong>, or a mismatch "
        "between instructional expertise and course requirements — not overall teaching effectiveness. "
        "It rules out a simple 'change the instructor' fix."
    ),
    cta=(
        "Review instructor–course alignment for Digital Marketing. Evaluate whether additional "
        "domain-specific support, curriculum adjustments, or co-teaching arrangements would "
        "improve student outcomes more than reassignment."
    ),
)

# --- Q2 ---
st.markdown('<div class="kf-section-h">Q2 · Score Distribution by Assessment Type</div>'
            '<div class="kf-section-sub">Where is performance most volatile? '
            'Platform-wide aggregate — not filterable by group/course.</div>',
            unsafe_allow_html=True)

df = type_stats()
if not df.empty:
    st.plotly_chart(chart_q2_type_stats(df), use_container_width=True)

render_insight_cta(
    insight=(
        "<strong>Assignments</strong> are the primary academic weakness across the platform — "
        "scoring substantially lower than exams, quizzes, or practicals. The issue is most "
        "severe in Digital Marketing, where assignment scores average only <strong>53.7%</strong>. "
        "Combined with low attendance, low mastery, and the highest late-submission rate, "
        "Digital Marketing appears to be the main driver of poor assignment outcomes."
    ),
    cta=(
        "Review assignment structure in Digital Marketing — workload, grading criteria, "
        "instructions, deadlines. Introduce milestone-based assignments, earlier feedback "
        "cycles, and targeted academic support to improve assignment completion and overall "
        "course performance."
    ),
)

# --- Q4 ---
st.markdown('<div class="kf-section-h">Q4 · Average Grade by Attendance Band</div>'
            '<div class="kf-section-sub">How strong is the relationship between attendance and grade?</div>',
            unsafe_allow_html=True)

if master_filtered is not None and not master_filtered.empty:
    st.plotly_chart(chart_q4_attendance_band(master_filtered), use_container_width=True)
else:
    st.info("No students match the current filters.")

render_insight_cta(
    insight=(
        "Students in the highest attendance band (<strong>80–100%</strong>) achieve an "
        "average grade of <strong>73.6%</strong>, compared with just <strong>62.0%</strong> "
        "among students attending 40–60% of sessions. The 11.6-point gap makes attendance "
        "one of the strongest predictors of academic success on the platform."
    ),
    cta=(
        "Implement early-warning attendance monitoring. Trigger an intervention when "
        "attendance falls below <strong>60%</strong> — the analysis shows a clear "
        "performance decline beyond this threshold, making it an effective point for "
        "proactive academic support."
    ),
)

# --- Q8 ---
st.markdown('<div class="kf-section-h">Q8 · Late Submissions vs Score</div>'
            '<div class="kf-section-sub">Do procrastinators score lower? '
            'Platform-wide aggregate.</div>',
            unsafe_allow_html=True)

df = late_submission_impact()
if not df.empty:
    st.plotly_chart(chart_q8_late_vs_ontime(df), use_container_width=True)

render_insight_cta(
    insight=(
        "Students who submit on time score <strong>~5 points higher</strong> on average than "
        "students who submit late (67.1 vs 62.1). Across 4,500+ submissions, late behaviour "
        "emerges as a strong indicator of lower academic performance and learning risk."
    ),
    cta=(
        "Implement automated deadline reminders at <strong>7 days</strong>, "
        "<strong>3 days</strong>, and <strong>24 hours</strong> before each deadline, "
        "with extra targeting for students with repeated late submissions."
    ),
)
