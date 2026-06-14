"""Overview page — v3.

Keeps the navy hero KPI banner unchanged. Below it: Executive Summary card,
a two-column layout with Student Risk Distribution (donut) and Platform Health,
and a closing insight + recommended action block.

Goal of this page: 'How healthy is the platform overall?'
March 2026 analysis lives exclusively on the Engagement page.
"""
import base64
from pathlib import Path
import streamlit as st

from config import APP_NAME, FAVICON_PATH, LOGO_PATH
from auth import require_auth
from components.injector import inject_styles
from components.sidebar import (
    render_sidebar, apply_master_filters, is_any_filter_active,
    render_active_filter_chips,
)
from components.charts import chart_risk_donut
from components.observations import render_insight_cta
from utils.queries import kpi_overview, master


st.set_page_config(page_title=f"Overview · {APP_NAME}", page_icon=str(FAVICON_PATH),
                   layout="wide", initial_sidebar_state="expanded")
inject_styles()
require_auth()
filters = render_sidebar(active="overview")


def _logo_b64() -> str:
    return base64.b64encode(Path(LOGO_PATH).read_bytes()).decode()


# ---------- KPI calculation (unchanged) ----------
def _live_kpis() -> dict:
    if not is_any_filter_active(filters):
        return kpi_overview() or {}
    df = master()
    df = apply_master_filters(df, filters)
    if df is None or df.empty:
        return {"n_students": 0, "n_groups": 0, "n_courses": 0,
                "platform_avg_attendance_pct": 0, "platform_avg_grade": 0,
                "pct_at_risk": 0, "avg_failed_concepts": 0}
    return {
        "n_students": int(df["student_id"].nunique()),
        "n_groups": int(df["group_id"].nunique()) if "group_id" in df.columns else 0,
        "n_courses": int(df["course_id"].nunique()) if "course_id" in df.columns else 0,
        "platform_avg_attendance_pct": round(df["attendance_rate"].mean() * 100, 1)
            if "attendance_rate" in df.columns else 0,
        "platform_avg_grade": round(df["avg_grade"].mean(), 1)
            if "avg_grade" in df.columns else 0,
        "pct_at_risk": round((df.get("cluster", 0) == 1).mean() * 100, 1)
            if "cluster" in df.columns else 0,
        "avg_failed_concepts": round(df["num_failed_concepts"].mean(), 1)
            if "num_failed_concepts" in df.columns else 0,
    }


kpi = _live_kpis()
title = "Platform Overview"
sub = ("The executive view of the Kayfa learning platform. "
       "Six headline KPIs and a snapshot of overall platform health.")
if is_any_filter_active(filters):
    sub = "Filtered view. KPIs and the population reflect your sidebar selections."

# ---------- HERO BANNER (unchanged) ----------
logo = _logo_b64()
st.markdown(
    f"""
    <div class="kf-hero">
      <div class="kf-hero-top">
        <div>
          <h1 class="kf-hero-title">{title}</h1>
          <div class="kf-hero-sub">{sub}</div>
        </div>
        <img class="kf-hero-logo" src="data:image/png;base64,{logo}" alt="Kayfa"/>
      </div>
      <div class="kf-hero-kpi-grid">
        <div class="kf-hero-kpi accent">
          <div class="kf-hero-kpi-label">Students</div>
          <div class="kf-hero-kpi-value">{kpi.get("n_students", 0):,}</div>
          <div class="kf-hero-kpi-hint">Active enrolments (G10 excluded)</div>
        </div>
        <div class="kf-hero-kpi">
          <div class="kf-hero-kpi-label">Groups</div>
          <div class="kf-hero-kpi-value">{kpi.get("n_groups", 0)}</div>
          <div class="kf-hero-kpi-hint">Viable cohorts</div>
        </div>
        <div class="kf-hero-kpi">
          <div class="kf-hero-kpi-label">Courses</div>
          <div class="kf-hero-kpi-value">{kpi.get("n_courses", 0)}</div>
          <div class="kf-hero-kpi-hint">Across 5 categories</div>
        </div>
        <div class="kf-hero-kpi success">
          <div class="kf-hero-kpi-label">Avg attendance</div>
          <div class="kf-hero-kpi-value">{kpi.get("platform_avg_attendance_pct", 0)}%</div>
          <div class="kf-hero-kpi-hint">Target ≥ 80%</div>
        </div>
        <div class="kf-hero-kpi warning">
          <div class="kf-hero-kpi-label">Avg grade</div>
          <div class="kf-hero-kpi-value">{kpi.get("platform_avg_grade", 0)}</div>
          <div class="kf-hero-kpi-hint">Out of 100</div>
        </div>
        <div class="kf-hero-kpi danger">
          <div class="kf-hero-kpi-label">At-risk share</div>
          <div class="kf-hero-kpi-value">{kpi.get("pct_at_risk", 0)}%</div>
          <div class="kf-hero-kpi-hint">Avg {kpi.get("avg_failed_concepts", 0)} failed concepts</div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

render_active_filter_chips(filters)


# ---------- EXECUTIVE SUMMARY ----------
attendance_pct = kpi.get("platform_avg_attendance_pct", 0)
avg_grade = kpi.get("platform_avg_grade", 0)
pct_at_risk = float(kpi.get("pct_at_risk", 0))

st.markdown(
    f"""
    <div class="kf-exec-summary">
      <div class="kf-exec-title">Executive Summary</div>
      <ul class="kf-exec-list">
        <li><span class="kf-dot kf-dot-green"></span>
            Average grade remains stable at <strong>{avg_grade}</strong></li>
        <li><span class="kf-dot kf-dot-green"></span>
            Student attendance is relatively strong at
            <strong>{attendance_pct}%</strong></li>
        <li><span class="kf-dot kf-dot-amber"></span>
            Attendance remains below the <strong>80%</strong> target</li>
        <li><span class="kf-dot kf-dot-amber"></span>
            <strong>{pct_at_risk}%</strong> of students are classified as at risk</li>
        <li><span class="kf-dot kf-dot-red"></span>
            Academic risk is concentrated in <strong>Digital Marketing</strong>
            and <strong>Recursion</strong></li>
        <li><span class="kf-dot kf-dot-blue"></span>
            Targeted interventions are expected to generate greater impact than
            broad platform-wide initiatives</li>
      </ul>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------- DONUT + PLATFORM HEALTH ----------
col_l, col_r = st.columns([3, 2], gap="large")

with col_l:
    st.plotly_chart(chart_risk_donut(pct_at_risk), use_container_width=True)

with col_r:
    # Status logic — keep simple, rule-based
    grade_status = "Stable" if avg_grade >= 60 else "Below Target"
    att_status = "On Target" if attendance_pct >= 80 else "Below Target"
    if pct_at_risk < 15:
        risk_status, risk_class = "Low", "kf-status-green"
    elif pct_at_risk < 25:
        risk_status, risk_class = "Moderate", "kf-status-amber"
    else:
        risk_status, risk_class = "High", "kf-status-red"

    grade_class = "kf-status-green" if grade_status == "Stable" else "kf-status-amber"
    att_class = "kf-status-green" if att_status == "On Target" else "kf-status-amber"

    st.markdown(
        f"""
        <div class="kf-health-card">
          <div class="kf-health-title">Platform Health</div>
          <div class="kf-health-row">
            <div class="kf-health-label">Grades</div>
            <div class="kf-health-dots"></div>
            <div class="kf-health-value {grade_class}">{grade_status}</div>
          </div>
          <div class="kf-health-row">
            <div class="kf-health-label">Attendance</div>
            <div class="kf-health-dots"></div>
            <div class="kf-health-value {att_class}">{att_status}</div>
          </div>
          <div class="kf-health-row">
            <div class="kf-health-label">Risk Level</div>
            <div class="kf-health-dots"></div>
            <div class="kf-health-value {risk_class}">{risk_status}</div>
          </div>
          <div class="kf-health-note">
            The platform is performing at a generally healthy level.
            Academic risk is concentrated in a small number of courses and
            concepts rather than being distributed across the platform.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------- INSIGHT + RECOMMENDED ACTION ----------
render_insight_cta(
    insight=(
        "The platform is operating at a generally healthy level, with stable "
        "grades and attendance across most cohorts. However, attendance remains "
        "below the 80% target and more than one in five students are classified "
        "as at risk. Academic challenges are concentrated in a small number of "
        "courses and concepts rather than being distributed across the platform."
    ),
    cta=(
        "Prioritize interventions around the highest-impact problem areas. "
        "Focus on improving attendance, addressing Digital Marketing performance "
        "issues, and redesigning high-failure concepts such as Recursion. "
        "Continue monitoring attendance and engagement as leading indicators of "
        "future academic risk."
    ),
)
