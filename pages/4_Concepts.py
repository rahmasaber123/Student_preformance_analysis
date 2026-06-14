"""Concepts page — Q6 · Pass/Fail root-cause · Q7 mastery trend.

v3: adds the Passed-vs-Failed chart that shows behavioural factors (attendance,
engagement, late submission) are statistically indistinguishable between
students who pass concepts and students who fail them — the visual basis for
the 'this is content design, not student behavior' conclusion.
"""
import streamlit as st

from config import APP_NAME, FAVICON_PATH
from auth import require_auth
from components.injector import inject_styles
from components.cards import render_page_header
from components.sidebar import (
    render_sidebar, filter_by_course, render_active_filter_chips,
)
from components.charts import (
    chart_q6_concept_failures,
    chart_passed_vs_failed,
    chart_recursion_by_instructor,
    chart_q7_concept_timeline,
)
from components.observations import render_insight_cta
from utils.queries import concept_failures, concept_mastery_timeline


st.set_page_config(page_title=f"Concepts · {APP_NAME}", page_icon=str(FAVICON_PATH),
                   layout="wide", initial_sidebar_state="expanded")
inject_styles()
require_auth()
filters = render_sidebar(active="concepts")

render_page_header(
    "Concepts",
    "Curriculum weak spots — which concepts students fail, and whether mastery is improving.",
)
render_active_filter_chips(filters)

# --- Q6 ---
st.markdown('<div class="kf-section-h">Q6 · Concepts with the Highest Failure Rate</div>'
            '<div class="kf-section-sub">Top 10 failing concepts across the platform.</div>',
            unsafe_allow_html=True)

df = concept_failures()
df = filter_by_course(df, filters, "course_id")
if not df.empty:
    st.plotly_chart(chart_q6_concept_failures(df), use_container_width=True)
else:
    st.info("No concepts match the current filters.")

render_insight_cta(
    insight=(
        "Student performance issues are not primarily driven by attendance, engagement, or "
        "submission behaviour. The data shows a small set of high-complexity concepts — "
        "particularly <strong>Recursion</strong> (85% failure rate) and several "
        "<strong>Digital Marketing</strong> topics (Funnel Analytics, SEO Basics, Content "
        "Strategy, Paid Ads) — are acting as learning bottlenecks."
    ),
    cta=(
        "<strong>1) Launch a Recursion intervention:</strong> visual recursion walkthroughs, "
        "step-by-step exercises, extra lab sessions, prerequisite checkpoints, practice "
        "quizzes before graded assessments.<br>"
        "<strong>2) Redesign Digital Marketing assessments:</strong> real-world case studies, "
        "more formative assessments, concept-specific learning resources.<br>"
        "<strong>3) Stand up concept-risk monitoring:</strong> auto-flag any concept whose "
        "failure rate exceeds 30%."
    ),
)

# --- Q6 deep-dive: Passed vs Failed Across Key Factors ---
st.markdown('<div class="kf-section-h">Q6 deep-dive · Passed vs Failed Students Across Key Factors</div>'
            '<div class="kf-section-sub">If concept failures were caused by student behaviour, '
            'we would expect failed students to attend less, engage less, and submit later. '
            'They don\'t.</div>',
            unsafe_allow_html=True)

st.plotly_chart(chart_passed_vs_failed(), use_container_width=True)

render_insight_cta(
    insight=(
        "Across the three behavioural factors we can measure, students who <strong>failed</strong> "
        "concepts are <strong>nearly indistinguishable</strong> from students who passed: "
        "attendance is 76.9% vs 80.2%, engagement events 61.1 vs 66.4, and late-submission rate "
        "is essentially identical at 57.4% vs 55.7%. The differences are too small to explain an "
        "85% failure rate on Recursion or the cluster of failures in Digital Marketing. "
        "This rules out behavioural causes and points decisively at <strong>content design</strong> — "
        "the concept itself, its assessment, or the prerequisites students are bringing to it."
    ),
    cta=(
        "Stop targeting tutoring and outreach at failing students for these concepts — the data "
        "does not support behaviour as the cause. Redirect that effort into "
        "<strong>content redesign</strong>: rebuild the Recursion module, audit the May assessment, "
        "and rework the four Digital Marketing concepts with case studies and formative checks. "
        "Behavioural interventions can continue for general academic risk (see the Engagement and "
        "At Risk pages) — but for these specific concepts, the fix is on the curriculum side."
    ),
)

# --- Q6/Q7 bridge: Recursion deep-dive ---
st.markdown('<div class="kf-section-h">Q7 deep-dive · Recursion failure rate by instructor</div>'
            '<div class="kf-section-sub">Two instructors teach Recursion. Bars show how many '
            'students failed; the line shows the failure rate. Even the better-performing '
            'instructor sits above 82%.</div>',
            unsafe_allow_html=True)

st.plotly_chart(chart_recursion_by_instructor(), use_container_width=True)

render_insight_cta(
    insight=(
        "Both instructors teaching Recursion show failure rates above 80% — "
        "<strong>Dr. Laila ElBaz at 88.9%</strong> (160 failed students) and "
        "<strong>Eng. Hossam Refaat at 82.5%</strong> (189 failed students). "
        "The 6.4-point spread shows some variation between instructors, but both "
        "rates are <strong>catastrophic</strong> — far above the 30% threshold that "
        "should trigger curriculum review. Hossam's higher failed count is a "
        "volume effect (he teaches more students), not a quality effect — his "
        "<em>rate</em> is actually the lower of the two. The pattern confirms "
        "the issue is content design, not teaching: even the higher-performing "
        "instructor's students fail Recursion 4 times out of 5."
    ),
    cta=(
        "Treat Recursion as a curriculum-redesign problem. Coaching the lower "
        "performer up to the higher performer's level would still leave 82.5% "
        "of students failing — so the lever isn't instructor quality, it's the "
        "concept itself. Redesign the module with visual recursion trees, "
        "step-by-step execution traces, an interactive simulator, and a "
        "prerequisite refresher on functions and call-stack behavior. Apply the "
        "redesign across <strong>both</strong> instructors simultaneously."
    ),
)

# --- Q7 ---
df = concept_mastery_timeline()
concept_name = df["concept_name"].iloc[0] if not df.empty and "concept_name" in df.columns else "Weakest Concept"

st.markdown(f'<div class="kf-section-h">Q7 · {concept_name} — Mastery Over Time</div>'
            '<div class="kf-section-sub">Is the cohort improving on this concept, holding flat, or getting worse? '
            'Platform-wide trend for the weakest concept.</div>',
            unsafe_allow_html=True)

if not df.empty:
    st.plotly_chart(chart_q7_concept_timeline(df, concept_name), use_container_width=True)

render_insight_cta(
    insight=(
        f"<strong>{concept_name}</strong> improved steadily from December through April — "
        "failure rates fell from 91% to 70%, average scores climbed. May regressed sharply: "
        "failure rates back to 86%, scores down. This looks like a sudden change rather than "
        "a long-term trend. Both Python Programming groups recorded &gt;80% failure rates "
        "despite different instructors, suggesting Recursion is a systemic learning challenge "
        "in the concept itself or its assessment, not an instructor-specific issue."
    ),
    cta=(
        "<strong>1) Redesign the Recursion module:</strong> visual recursion trees, "
        "step-by-step execution traces, interactive simulators, prerequisite refresher on "
        "functions and stack behaviour.<br>"
        "<strong>2) Audit the May assessment:</strong> was the exam changed? new questions? "
        "difficulty increased? The May decline appears simultaneously across both groups, so "
        "isolate whether it came from content or assessment design."
    ),
)
