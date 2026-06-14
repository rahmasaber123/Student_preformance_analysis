"""Groups page — Q1 attendance · Q12 enrolment · Q15 trajectory · Q13 merge.

v2: every chart respects the sidebar filters; active-filter chips shown at top.
"""
import streamlit as st

from config import APP_NAME, FAVICON_PATH
from auth import require_auth
from components.injector import inject_styles
from components.cards import render_page_header
from components.sidebar import (
    render_sidebar, filter_by_group, render_active_filter_chips,
)
from components.charts import (
    chart_q1_attendance,
    chart_q12_group_sizes,
    chart_q15_grade_trends,
    chart_q13_merge_comparison,
)
from components.observations import render_insight_cta
from utils.queries import (
    group_attendance,
    group_sizes,
    grade_trends,
    group_merge_recommendation,
)


st.set_page_config(page_title=f"Groups · {APP_NAME}", page_icon=str(FAVICON_PATH),
                   layout="wide", initial_sidebar_state="expanded")
inject_styles()
require_auth()
filters = render_sidebar(active="groups")

render_page_header(
    "Groups",
    "Attendance, enrolment integrity, trajectory, and viability across all groups.",
)
render_active_filter_chips(filters)


# --- Q1 ---
st.markdown('<div class="kf-section-h">Q1 · Attendance Rate by Group</div>'
            '<div class="kf-section-sub">Which groups sit below the platform average?</div>',
            unsafe_allow_html=True)

df = group_attendance()
df = filter_by_group(df, filters, "group_id")
if not df.empty:
    st.plotly_chart(chart_q1_attendance(df), use_container_width=True)
else:
    st.info("No groups match the current filters.")

render_insight_cta(
    insight=(
        "The platform-wide attendance rate is <strong>75.8%</strong>. Two groups sit well "
        "below average: <strong>Group 07 (Digital Marketing)</strong> at 60.2% and "
        "<strong>Group 10 (Cybersecurity)</strong> at 65.4%. G10 is later shown to be a "
        "data-integrity outlier; G07 represents a real attendance problem."
    ),
    cta=(
        "Prioritise <strong>Group 07</strong>. Review the instructor, scheduling, and "
        "student-participation patterns. Contact students with repeated absences and "
        "pair the intervention with the Digital Marketing concept-redesign work surfaced "
        "on the Concepts page."
    ),
)

# --- Q12 ---
st.markdown('<div class="kf-section-h">Q12 · Stated vs Actual Group Sizes</div>'
            '<div class="kf-section-sub">Enrolment discrepancies that should be validated before group-level KPIs are trusted.</div>',
            unsafe_allow_html=True)

df = group_sizes()
df = filter_by_group(df, filters, "group_id")
if not df.empty:
    st.plotly_chart(chart_q12_group_sizes(df), use_container_width=True)
else:
    st.info("No groups match the current filters.")

render_insight_cta(
    insight=(
        "Four groups show enrolment discrepancies between recorded and actual student counts. "
        "The largest issue is <strong>Group 10</strong>: only one active student was found "
        "despite the group being registered with 31 students. Enrolment records are not "
        "synchronised across datasets and should be validated before relying on group-level KPIs."
    ),
    cta=(
        "Reconcile <code>stated_num_students</code> in <code>groups.csv</code> against the "
        "live enrolment in <code>students.csv</code>. Treat any group flagged here as "
        "unreliable until resolved, and exclude small cohorts (n &lt; 20) from benchmarking."
    ),
)

# --- Q15 ---
st.markdown('<div class="kf-section-h">Q15 · Group Performance Trend</div>'
            '<div class="kf-section-sub">Monthly grade-change slope per group, G10 excluded as an outlier.</div>',
            unsafe_allow_html=True)

df = grade_trends()
df = filter_by_group(df, filters, "Group")
if not df.empty:
    st.plotly_chart(chart_q15_grade_trends(df), use_container_width=True)
else:
    st.info("No groups match the current filters.")

render_insight_cta(
    insight=(
        "After excluding G10, <strong>7 of 9 groups</strong> show a declining trend; "
        "only <strong>G08 (+0.09)</strong> and <strong>G04 (+0.02)</strong> are flat or "
        "improving. Steepest declines: G09 (-0.43), G01 (-0.41), G02 (-0.35), G06 (-0.35) "
        "points/month. This is systemic, not isolated."
    ),
    cta=(
        "Run root-cause analysis on the four steepest decliners (G09, G01, G02, G06) — "
        "attendance, engagement, completion, concept mastery. Replicate the practices of "
        "G08 and G04 (instructor methods, engagement, assessment design) across struggling "
        "groups. Add monthly monitoring that flags any group below -0.30 pts/month."
    ),
)

# --- Q13 ---
st.markdown('<div class="kf-section-h">Q13 · Non-Viable Group — Merge Recommendation</div>'
            '<div class="kf-section-sub">G10 has only one active student; we matched them by concept profile to a peer in another group.</div>',
            unsafe_allow_html=True)

rec = group_merge_recommendation() or {}
if rec:
    st.plotly_chart(chart_q13_merge_comparison(rec), use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Non-viable group", rec.get("non_viable_group_id", "—"))
    c2.metric("Recommended target", rec.get("recommended_target_group_id", "—"))
    c3.metric("Similarity", f'{rec.get("similarity_score", 0):.3f}')

    render_insight_cta(
        insight=(
            f"G10 has a single student (<strong>{rec.get('non_viable_student_name','')}</strong>), "
            f"making it operationally non-viable. The closest concept-profile match is "
            f"<strong>{rec.get('matched_student_name','')}</strong> in "
            f"<strong>{rec.get('recommended_target_group_id','')}</strong>, with a similarity "
            f"score of {rec.get('similarity_score', 0):.3f}."
        ),
        cta=(
            f"<strong>Dissolve G10 immediately.</strong> Transfer "
            f"{rec.get('non_viable_student_name','the G10 student')} into "
            f"<strong>{rec.get('recommended_target_group_id','')}</strong> where their "
            f"concept strengths and gaps already mirror the cohort — zero academic disruption, "
            f"and the platform saves one instructor slot."
        ),
    )
