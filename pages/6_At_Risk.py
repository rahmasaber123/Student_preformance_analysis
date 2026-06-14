"""At Risk page — Q14 top-10 risk · Q14 course concentration · Q11 segments.

v2: at-risk list respects group/course/instructor filters; chips at top.
"""
import streamlit as st

from config import APP_NAME, FAVICON_PATH
from auth import require_auth
from components.injector import inject_styles
from components.cards import render_page_header
from components.sidebar import (
    render_sidebar, render_active_filter_chips, is_any_filter_active,
    apply_master_filters,
)
from components.charts import (
    chart_q14_top_at_risk,
    chart_q14_course_concentration,
    chart_q11_segments,
    chart_risk_concentration_by_group,
)
from components.observations import render_insight_cta
from utils.queries import at_risk, cluster_profiles, master


st.set_page_config(page_title=f"At Risk · {APP_NAME}", page_icon=str(FAVICON_PATH),
                   layout="wide", initial_sidebar_state="expanded")
inject_styles()
require_auth()
filters = render_sidebar(active="at_risk")

render_page_header(
    "At Risk",
    "The students an instructor should contact first — and the segments behind them.",
)
render_active_filter_chips(filters)

# --- Q14 ---
st.markdown('<div class="kf-section-h">Q14 · Top 10 At-Risk Students</div>'
            '<div class="kf-section-sub">Composite risk score: attendance, grade, engagement, and failed concepts.</div>',
            unsafe_allow_html=True)

df = at_risk()

# Apply group / course / instructor filters to the at-risk list
if df is not None and not df.empty:
    if filters.get("groups") and "group_name" in df.columns:
        m = master()
        if not m.empty and {"group_id", "group_name"}.issubset(m.columns):
            gid_to_gname = dict(zip(m["group_id"].astype(str), m["group_name"].astype(str)))
            allowed_names = {gid_to_gname[g] for g in filters["groups"] if g in gid_to_gname}
            df = df[df["group_name"].astype(str).isin(allowed_names)]
    if filters.get("courses") and "course_name" in df.columns:
        m = master()
        if not m.empty and {"course_id", "course_name"}.issubset(m.columns):
            cid_to_cname = dict(zip(m["course_id"].astype(str), m["course_name"].astype(str)))
            allowed = {cid_to_cname[c] for c in filters["courses"] if c in cid_to_cname}
            df = df[df["course_name"].astype(str).isin(allowed)]
    if filters.get("instructors") and "student_id" in df.columns:
        m = master()
        if not m.empty and "instructor" in m.columns:
            allowed_ids = set(m[m["instructor"].isin(filters["instructors"])]["student_id"]
                                .astype(str).tolist())
            df = df[df["student_id"].astype(str).isin(allowed_ids)]

if df is not None and not df.empty:
    c1, c2 = st.columns([5, 4])
    with c1:
        st.plotly_chart(chart_q14_top_at_risk(df), use_container_width=True)
    with c2:
        st.plotly_chart(chart_q14_course_concentration(df), use_container_width=True)

    with st.expander("View at-risk list (detail)"):
        cols = [c for c in ["full_name", "group_name", "course_name",
                            "attendance_rate", "avg_grade", "num_failed_concepts"]
                if c in df.columns]
        st.dataframe(df[cols], use_container_width=True, hide_index=True)
else:
    st.info("No at-risk students match the current filters.")

render_insight_cta(
    insight=(
        "<strong>8 of the top 10 at-risk students are in Digital Marketing (Group 07 — C005).</strong> "
        "This isn't a student problem — it's a course/group problem. Average grade in this group "
        "is below 50, attendance hovers around 50%, and failed concepts average 18+. The single "
        "outlier (Python Programming) confirms this is course-specific, not platform-wide."
    ),
    cta=(
        "Digital Marketing needs an urgent intervention — not individual outreach, but a "
        "<strong>course-level audit</strong>. Investigate whether instructor, curriculum "
        "difficulty, or assessment design is driving failure. Contacting these 10 students "
        "without fixing the course will just produce 10 more at-risk students next term. "
        "<strong>Short-term:</strong> instructor check-in this week. "
        "<strong>Medium-term:</strong> redesign assessments with the highest concept failure "
        "rates in C005."
    ),
)

# --- Q11 ---
st.markdown('<div class="kf-section-h">Q11 · Student Segmentation</div>'
            '<div class="kf-section-sub">K-Means clustering on attendance, grade, engagement, and failed concepts. G10 excluded. '
            'Platform-wide model — not filterable.</div>',
            unsafe_allow_html=True)

profiles = cluster_profiles()
if not profiles.empty:
    st.plotly_chart(chart_q11_segments(profiles), use_container_width=True)

render_insight_cta(
    insight=(
        "<strong>⭐ High Achievers (199):</strong> highest attendance (85%), highest "
        "engagement (73 events), highest grade (76), fewest failed concepts (3). "
        "<strong>⚠️ Needs Attention (103):</strong> lowest attendance (67%), lowest grades "
        "(59), 12.6 failed concepts on average — at greatest risk. "
        "<strong>📊 Average Performers (197):</strong> solid attendance (74%) and grades (71); "
        "the largest opportunity for improvement since they sit just below the top segment."
    ),
    cta=(
        "<strong>Replicate</strong> the behaviors of High Achievers through peer mentoring "
        "and study groups. <strong>Intervene</strong> with the Needs Attention segment via "
        "tutoring, support sessions, and proactive outreach before final assessments. "
        "<strong>Nudge</strong> Average Performers — small improvements in engagement and "
        "attendance could move a large share of them into the top segment, producing the "
        "largest overall gain in institutional performance."
    ),
)

# --- Q11 Extension · Risk Concentration by Group ---
st.markdown('<div class="kf-section-h">Q11 Extension · Risk Concentration by Group</div>'
            '<div class="kf-section-sub">Where the 103 Needs-Attention students actually sit. '
            'A few groups carry most of the load.</div>',
            unsafe_allow_html=True)

master_df = master()
master_df = apply_master_filters(master_df, filters)

if master_df is not None and not master_df.empty:
    st.plotly_chart(chart_risk_concentration_by_group(master_df),
                    use_container_width=True)
else:
    st.info("No students match the current filters.")

render_insight_cta(
    insight=(
        "⚠️ Student risk is highly concentrated rather than evenly distributed. "
        "<strong>Group 07 accounts for 40 of the 103 students in the Needs Attention "
        "segment (38.8%)</strong>, making it the single largest contributor to academic "
        "risk across the platform. No other group contributes more than 15 students, "
        "highlighting a significant concentration of performance challenges within a "
        "single cohort. Notably, Group 07 belongs to the <strong>Digital Marketing</strong> "
        "course led by <strong>Eng. Hossam Refaat</strong>, suggesting that further "
        "investigation into attendance patterns, engagement levels, instructional delivery, "
        "and concept difficulty within this cohort may be warranted."
    ),
    cta=(
        "🎯 <strong>Prioritize Group 07 for immediate intervention.</strong> Since nearly "
        "four out of every ten at-risk students belong to this group, a targeted review "
        "involving the instructor, curriculum content, attendance behavior, and student "
        "engagement metrics could significantly reduce platform-wide academic risk and "
        "improve overall learning outcomes."
    ),
)
