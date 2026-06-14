"""Chart builders — each one mirrors the notebook code as closely as possible.

Functions are stateless: pass a DataFrame, get a styled Plotly figure.
"""
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from utils.helpers import (
    style_fig,
    add_attendance_band,
    add_engagement_quartile,
    add_age_band,
)
from config import BLUE, ACCENT_RED

def _month_label(series):
    """Coerce any month input (datetime, ISO string, period) into 'YYYY-MM'."""
    s = pd.to_datetime(series, errors="coerce")
    if s.notna().any():
        return s.dt.strftime("%Y-%m")
    return series.astype(str).str.slice(0, 7)
# =====================================================
# Q1 — Attendance Rate by Group
# =====================================================
def chart_q1_attendance(att_grp: pd.DataFrame) -> go.Figure:
    df = att_grp.sort_values("rate", ascending=True)
    platform_avg = df["rate"].mean()
    colors = [BLUE[0] if r < platform_avg else BLUE[4] for r in df["rate"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df["group_name"], x=df["rate"],
        orientation="h", marker_color=colors,
        text=df["rate"].apply(lambda x: f"<b>{x}%</b>"),
        textposition="outside",
        textfont=dict(size=12),
        showlegend=False,
    ))
    # legend proxies
    fig.add_trace(go.Bar(x=[None], y=[None], marker_color=BLUE[0],
                         name="Below platform average"))
    fig.add_trace(go.Bar(x=[None], y=[None], marker_color=BLUE[4],
                         name="At or above average"))

    fig.add_vline(
        x=platform_avg, line_dash="dash", line_color=ACCENT_RED, line_width=2.5,
    )
    fig.add_annotation(
        x=platform_avg, y=1.02, xref="x", yref="paper",
        text=f"<b>Platform Avg: {platform_avg:.1f}%</b>",
        showarrow=False, xanchor="center",
        bgcolor="rgba(255,255,255,0.95)",
        bordercolor=ACCENT_RED, borderwidth=1, borderpad=4,
        font=dict(size=11, color=ACCENT_RED),
    )
    style_fig(fig, "")
    fig.update_layout(
        yaxis_title="", xaxis_title="Attendance Rate (%)",
        xaxis_range=[20, 108],
        legend=dict(orientation="h", yanchor="bottom", y=-0.20,
                    xanchor="center", x=0.5),
    )
    return fig

# =====================================================
# Q2 — Score Distribution by Assessment Type
# =====================================================
def chart_q2_type_stats(type_stats: pd.DataFrame) -> go.Figure:
    df = type_stats.sort_values("avg_score", ascending=True)
    overall_avg = (df["avg_score"] * df["count"]).sum() / df["count"].sum()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df["type"], x=df["avg_score"],
        orientation="h", marker_color=BLUE[2],
        text=[f"<b>{v:.1f}</b>" for v in df["avg_score"]],
        textposition="inside",
        insidetextanchor="end",
        textfont=dict(color="white", size=14),
        showlegend=False,
    ))
    fig.add_vline(x=overall_avg, line_dash="dash",
                  line_color=ACCENT_RED, line_width=2.5)
    fig.add_annotation(
        text=f"<b>Overall Avg: {overall_avg:.1f}</b>",
        x=overall_avg, xref="x", y=1.0, yref="paper",
        xanchor="center", yanchor="bottom", showarrow=False,
        bgcolor="rgba(255,255,255,0.95)",
        bordercolor=ACCENT_RED, borderwidth=1, borderpad=4,
        font=dict(size=11, color=ACCENT_RED),
    )
    style_fig(fig, "")
    fig.update_layout(
        margin=dict(l=60, r=30, t=60, b=50),
        xaxis_title="Average Score", yaxis_title="Assessment Type",
        xaxis_range=[0, 110],
    )
    return fig

# =====================================================
# Q3 — Average Grade by Course
# =====================================================
def chart_q3_course_grade(course_stats: pd.DataFrame) -> go.Figure:
    df = course_stats.sort_values("mean")
    overall_avg = df["mean"].mean()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df["course_name"], x=df["mean"],
        orientation="h", marker_color=BLUE[2],
        text=[f"<b>{v:.1f}</b>" for v in df["mean"]],
        textposition="inside",
        insidetextanchor="end",
        textfont=dict(color="white", size=13),
        showlegend=False,
    ))
    fig.add_vline(x=overall_avg, line_dash="dash", line_color=ACCENT_RED, line_width=2.5)
    fig.add_annotation(
        text=f"<b>Avg: {overall_avg:.1f}</b>",
        x=overall_avg, xref="x", y=1.02, yref="paper",
        xanchor="center", yanchor="bottom", showarrow=False,
        bgcolor="rgba(255,255,255,0.95)",
        bordercolor=ACCENT_RED, borderwidth=1, borderpad=4,
        font=dict(size=11, color=ACCENT_RED),
    )
    style_fig(fig, "")
    fig.update_layout(
        yaxis_title="", xaxis_title="Average Grade",
        xaxis_range=[0, 100],
    )
    return fig


# =====================================================
# Q3 deep-dive — Average Student Grade by Instructor
# =====================================================
def chart_instructor_grade(master: pd.DataFrame) -> go.Figure:
    if master is None or master.empty or "instructor" not in master.columns:
        fig = go.Figure()
        style_fig(fig, "")
        fig.add_annotation(
            text="No instructor data available for the current selection.",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(color="#64748B", size=13),
        )
        return fig

    agg = (
        master.dropna(subset=["instructor", "avg_grade"])
              .groupby("instructor")["avg_grade"].mean()
              .reset_index().sort_values("avg_grade")
    )
    overall_avg = agg["avg_grade"].mean()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=agg["instructor"], y=agg["avg_grade"],
        marker_color=BLUE[2],
        text=[f"<b>{v:.1f}</b>" for v in agg["avg_grade"]],
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(color="white", size=14),
        showlegend=False,
    ))
    fig.add_hline(y=overall_avg, line_dash="dash", line_color=ACCENT_RED, line_width=2.5)
    fig.add_annotation(
        text=f"<b>Mean: {overall_avg:.1f}</b>",
        x=1, xref="paper", y=overall_avg, yref="y",
        xanchor="right", yanchor="bottom", showarrow=False,
        bgcolor="rgba(255,255,255,0.95)",
        bordercolor=ACCENT_RED, borderwidth=1, borderpad=4,
        font=dict(size=11, color=ACCENT_RED),
    )
    style_fig(fig, "")
    fig.update_layout(
        xaxis_title="Instructor", yaxis_title="Average Grade",
        yaxis_range=[0, 100], xaxis_tickangle=-25,
    )
    return fig


def chart_q4_attendance_band(master: pd.DataFrame) -> go.Figure:
    df = add_attendance_band(master)
    agg = (
        df.groupby("att_band", observed=True)
          .agg(avg_grade=("avg_grade", "mean"),
               students=("student_id", "count"))
          .reset_index()
    )
    avg = agg["avg_grade"].mean()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=agg["att_band"], y=agg["avg_grade"],
        marker_color=BLUE[2],
        text=[f"<b>{g:.1f}</b>" for g in agg["avg_grade"]],
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(color="white", size=14),
        showlegend=False,
    ))
    fig.add_hline(y=avg, line_dash="dash", line_color=ACCENT_RED, line_width=2.5)
    fig.add_annotation(
        text=f"<b>Mean: {avg:.1f}</b>",
        x=1, xref="paper", y=avg, yref="y",
        xanchor="right", yanchor="bottom", showarrow=False,
        bgcolor="rgba(255,255,255,0.95)",
        bordercolor=ACCENT_RED, borderwidth=1, borderpad=4,
        font=dict(size=11, color=ACCENT_RED),
    )
    style_fig(fig, "")
    fig.update_layout(
        xaxis_title="Attendance Band", yaxis_title="Average Grade",
        yaxis_range=[0, agg["avg_grade"].max() * 1.2],
    )
    return fig

# =====================================================
# Q5A — Avg Grade by Engagement Level
# =====================================================
def chart_q5a_engagement_grade(master: pd.DataFrame) -> go.Figure:
    df = add_engagement_quartile(master)
    agg = (
        df.groupby("eng_quartile", observed=True)
          .agg(avg_grade=("avg_grade", "mean"))
          .reset_index()
    )
    overall_avg = agg["avg_grade"].mean()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=agg["eng_quartile"], y=agg["avg_grade"],
        marker_color=BLUE[2],
        text=[f"<b>{v:.1f}</b>" for v in agg["avg_grade"]],
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(color="white", size=14),
        showlegend=False,
    ))
    fig.add_hline(y=overall_avg, line_dash="dash", line_color=ACCENT_RED, line_width=2.5)
    fig.add_annotation(
        text=f"<b>Overall Avg: {overall_avg:.1f}</b>",
        x=1, xref="paper", y=overall_avg, yref="y",
        xanchor="right", yanchor="bottom", showarrow=False,
        bgcolor="rgba(255,255,255,0.95)",
        bordercolor=ACCENT_RED, borderwidth=1, borderpad=4,
        font=dict(size=11, color=ACCENT_RED),
    )
    style_fig(fig, "")
    fig.update_layout(
        xaxis_title="Engagement Level", yaxis_title="Average Grade",
    )
    return fig

# =====================================================
# Q5B — Avg Platform Activity by Engagement Level
# =====================================================
def chart_q5b_engagement_activity(master: pd.DataFrame) -> go.Figure:
    df = add_engagement_quartile(master)
    agg = (
        df.groupby("eng_quartile", observed=True)
          .agg(avg_events=("total_events", "mean"))
          .reset_index()
    )

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=agg["eng_quartile"], y=agg["avg_events"],
        marker_color=BLUE[4],
        text=[f"<b>{v:.0f}</b>" for v in agg["avg_events"]],
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(color="white", size=14),
        showlegend=False,
    ))
    style_fig(fig, "")
    fig.update_layout(
        xaxis_title="Engagement Level",
        yaxis_title="Average Platform Events",
    )
    return fig

# =====================================================
# Q6 — Top 10 Concepts by Failure Rate
# =====================================================
def chart_q6_concept_failures(concept_fail: pd.DataFrame) -> go.Figure:
    top_fail = concept_fail.sort_values("fail_rate", ascending=False).head(10).copy()
    top_fail["label"] = top_fail["concept_name"] + " (" + top_fail["course_name"] + ")"
    top_fail = top_fail.sort_values("fail_rate", ascending=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=top_fail["label"], x=top_fail["fail_rate"],
        orientation="h", marker_color=BLUE[1],
        text=top_fail["fail_rate"].apply(lambda x: f"{x}%"),
        textposition="outside",
    ))
    style_fig(fig, "Q6: Top 10 Concepts by Failure Rate")
    fig.update_layout(
        yaxis_title="", xaxis_title="Failure Rate (%)",
        xaxis_range=[0, top_fail["fail_rate"].max() * 1.15],
        showlegend=False,
    )
    return fig


# =====================================================
# Q6 deep-dive — Passed vs Failed Students Across Key Factors
# =====================================================
def chart_passed_vs_failed(values: dict | None = None) -> go.Figure:
    """Compare three behavioural factors between students who passed vs
    failed the Digital Marketing concept cluster.

    Mirrors the notebook chart. Default values are the ones produced by
    the notebook's root-cause analysis; pass `values` to override.
    """
    if not values:
        values = {
            "factors": ["Attendance (%)", "Engagement Events", "Late Submission (%)"],
            "failed":  [76.9, 61.1, 57.4],
            "passed":  [80.2, 66.4, 55.7],
        }

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Failed",
        x=values["factors"], y=values["failed"],
        marker_color=BLUE[1],
        text=[f"{v:.1f}" for v in values["failed"]],
        textposition="outside",
    ))
    fig.add_trace(go.Bar(
        name="Passed",
        x=values["factors"], y=values["passed"],
        marker_color=BLUE[4],
        text=[f"{v:.1f}" for v in values["passed"]],
        textposition="outside",
    ))
    fig.update_layout(barmode="group")
    style_fig(fig, "Passed vs Failed Students Across Key Factors")
    fig.update_layout(
        xaxis_title="", yaxis_title="Value",
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="center", x=0.5, title=""),
    )
    return fig


# =====================================================
# Q10 — Outcomes by Age Band (split into 3 panels)
# =====================================================
def _age_band_aggregate(master: pd.DataFrame) -> pd.DataFrame:
    df = add_age_band(master)
    agg = (
        df.groupby("age_band", observed=True)
          .agg(avg_grade=("avg_grade", "mean"),
               attendance=("attendance_rate", lambda x: (x * 100).mean()),
               engagement=("total_events", "mean"),
               students=("student_id", "count"))
          .reset_index()
    )
    # ensure category order
    order = ["<20", "20-25", "26-30", "30+"]
    agg["age_band"] = pd.Categorical(agg["age_band"], categories=order, ordered=True)
    return agg.sort_values("age_band")


def _q10_panel(agg, value_col, ylabel, color, fmt, ymax):
    avg = agg[value_col].mean()
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=agg["age_band"].astype(str), y=agg[value_col],
        marker_color=color,
        text=[f"<b>{fmt(v)}</b>" for v in agg[value_col]],
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(color="white", size=14),
        showlegend=False,
    ))
    fig.add_hline(y=avg, line_dash="dash", line_color=ACCENT_RED, line_width=2.5)
    fig.add_annotation(
        text=f"<b>Mean: {fmt(avg)}</b>",
        x=1, xref="paper", y=avg, yref="y",
        xanchor="right", yanchor="bottom",
        showarrow=False,
        bgcolor="rgba(255,255,255,0.95)",
        bordercolor=ACCENT_RED, borderwidth=1, borderpad=4,
        font=dict(size=11, color=ACCENT_RED),
    )
    style_fig(fig, "")
    fig.update_layout(
        xaxis_title="", yaxis_title=ylabel, yaxis_range=[0, ymax],
    )
    return fig


def chart_q10_age_grade(master: pd.DataFrame) -> go.Figure:
    agg = _age_band_aggregate(master)
    return _q10_panel(agg, "avg_grade", "Avg Grade",
                      BLUE[1], lambda v: f"{v:.1f}",
                      max(100, agg["avg_grade"].max() * 1.15))


def chart_q10_age_attendance(master: pd.DataFrame) -> go.Figure:
    agg = _age_band_aggregate(master)
    return _q10_panel(agg, "attendance", "Attendance %",
                      BLUE[3], lambda v: f"{v:.1f}%", 100)


def chart_q10_age_engagement(master: pd.DataFrame) -> go.Figure:
    agg = _age_band_aggregate(master)
    return _q10_panel(agg, "engagement", "Avg Events",
                      BLUE[4], lambda v: f"{v:.0f}",
                      agg["engagement"].max() * 1.2)
# =====================================================
# Overview — Student Risk Distribution donut
# =====================================================
def chart_risk_donut(pct_at_risk: float) -> go.Figure:
    healthy = max(0.0, 100.0 - float(pct_at_risk))
    at_risk = float(pct_at_risk)
    fig = go.Figure(go.Pie(
        labels=["Healthy Students", "At-Risk Students"],
        values=[healthy, at_risk],
        hole=0.55,
        marker=dict(colors=[BLUE[2], ACCENT_RED]),
        textinfo="label+percent",
        textposition="outside",
        sort=False,
    ))
    style_fig(fig, "Student Risk Distribution")
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15,
                    xanchor="center", x=0.5),
        annotations=[dict(
            text=f"<b>{healthy:.1f}%</b><br><span style='font-size:11px;color:#64748B'>Healthy</span>",
            x=0.5, y=0.5, font=dict(size=22, color="#0F172A"),
            showarrow=False,
        )],
        margin=dict(l=20, r=20, t=60, b=40),
    )
    return fig

# =====================================================
# Performance deep-dive — Hossam Refaat grade by course
# =====================================================
def chart_hossam_pie(master: pd.DataFrame,
                     instructor_name: str = "Eng. Hossam Refaat") -> go.Figure:
    """Average grade per course for a single instructor, with a clear takeaway."""
    fig = go.Figure()
    if master is None or master.empty or "instructor" not in master.columns:
        style_fig(fig, "")
        fig.add_annotation(text="No instructor data available.",
                           xref="paper", yref="paper", x=0.5, y=0.5,
                           showarrow=False, font=dict(color="#64748B"))
        return fig

    sub = master[master["instructor"] == instructor_name]
    if sub.empty or "course_name" not in sub.columns:
        style_fig(fig, "")
        fig.add_annotation(text=f"No students under {instructor_name}.",
                           xref="paper", yref="paper", x=0.5, y=0.5,
                           showarrow=False, font=dict(color="#64748B"))
        return fig

    agg = (
        sub.groupby("course_name")
           .agg(students=("student_id", "count"),
                avg_grade=("avg_grade", "mean"))
           .reset_index()
           .sort_values("avg_grade", ascending=True)
    )
    platform_avg = float(sub["avg_grade"].mean())
    colors = [ACCENT_RED if g < 65 else BLUE[1] for g in agg["avg_grade"]]

    fig.add_trace(go.Bar(
        y=agg["course_name"], x=agg["avg_grade"],
        orientation="h", marker_color=colors,
        text=[f"<b>{g:.1f}</b>" for g in agg["avg_grade"]],
        textposition="inside",
        insidetextanchor="end",
        textfont=dict(color="white", size=16),
        showlegend=False,
    ))
    fig.add_vline(x=platform_avg, line_dash="dash",
                  line_color="#64748B", line_width=2.5)
    fig.add_annotation(
        text=f"<b>His overall avg: {platform_avg:.1f}</b>",
        x=platform_avg, xref="x", y=1.05, yref="paper",
        xanchor="center", yanchor="bottom", showarrow=False,
        bgcolor="rgba(255,255,255,0.95)",
        bordercolor="#64748B", borderwidth=1, borderpad=4,
        font=dict(size=11, color="#475569"),
    )

    

    style_fig(fig, "")
    fig.update_layout(
        xaxis_title="Average Grade",
        yaxis_title="",
        xaxis_range=[0, 100],
        margin=dict(l=20, r=40, t=60, b=100),
    )
    return fig
# =====================================================
# Concepts deep-dive — Recursion Performance Across Python Groups
# =====================================================
def chart_recursion_by_group(master: pd.DataFrame | None = None) -> go.Figure:
    """The notebook's recursion_group chart — Python Group 03 vs Group 04.

    Uses notebook values as defaults since the recursion-specific scores are
    not stored as a precomputed Atlas collection.
    """
    # Notebook values for Recursion avg score per Python group
    data = pd.DataFrame({
        "group_name": ["Python Group 03", "Python Group 04"],
        "avg_score":  [13.7, 14.0],
    })

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=data["group_name"], y=data["avg_score"],
        marker_color=BLUE[2],
        text=data["avg_score"].round(1),
        textposition="outside",
    ))
    style_fig(fig, "Recursion Performance Across Python Groups")
    fig.update_layout(
        xaxis_title="", yaxis_title="Average Recursion Score (%)",
        yaxis_range=[0, 100], showlegend=False,
    )
    return fig

# =====================================================
# Concepts deep-dive — Recursion Failures by Instructor
# =====================================================
def chart_recursion_by_instructor() -> go.Figure:
    """Mirrors the notebook's recursion_rate chart exactly.

    Values are hardcoded from the notebook's `recursion_rate` dataframe
    (the raw `concepts_performance` data isn't stored in Atlas as a
    standalone collection, so we can't recompute it on the fly here).
    Sorted by failure_rate descending — same as the notebook.
    """
    recursion_rate = pd.DataFrame({
        "instructor":   ["Dr. Laila ElBaz", "Eng. Hossam Refaat"],
        "total":        [180, 229],
        "failed":       [160, 189],
        "failure_rate": [88.9, 82.5],
    })

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Bar(
        x=recursion_rate["instructor"],
        y=recursion_rate["failed"],
        name="Failed Students",
        marker_color=BLUE[3],
        text=recursion_rate["failed"], textposition="outside",
        opacity=0.85,
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        x=recursion_rate["instructor"],
        y=recursion_rate["failure_rate"],
        mode="lines+markers+text",
        text=recursion_rate["failure_rate"].apply(lambda x: f"{x}%"),
        textposition="top center", textfont=dict(size=13, color=BLUE[0]),
        line=dict(color=BLUE[0], width=3),
        marker=dict(size=10, color=BLUE[0]),
        name="Failure Rate %",
    ), secondary_y=True)

    style_fig(fig, "Recursion Failures by Instructor")
    fig.update_yaxes(title_text="Failed Students", secondary_y=False)
    fig.update_yaxes(title_text="Failure Rate (%)", secondary_y=True, showgrid=False)
    fig.update_layout(
        xaxis_title="",
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="center", x=0.5),
    )
    return fig


# =====================================================
# Q7 — Weakest Concept Mastery Over Time
# =====================================================
def chart_q7_concept_timeline(timeline: pd.DataFrame, concept_name: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=timeline["month"], y=timeline["avg_score"],
        mode="lines+markers",
        line=dict(color=BLUE[2], width=3),
        marker=dict(size=10), name="Avg Score",
    ))
    fig.add_trace(go.Scatter(
        x=timeline["month"], y=timeline["fail_rate"],
        mode="lines+markers",
        line=dict(color=ACCENT_RED, width=2, dash="dash"),
        marker=dict(size=8), name="Fail Rate %",
    ))
    style_fig(fig, f"Q7: {concept_name} — Mastery Trend Over Time")
    fig.update_layout(xaxis_title="Month", yaxis_title="%")
    return fig


# =====================================================
# Q8 — On-Time vs Late Submissions
# =====================================================
def chart_q8_late_vs_ontime(late_impact: pd.DataFrame) -> go.Figure:
    on_row = late_impact[late_impact["label"] == "On Time"].iloc[0]
    late_row = late_impact[late_impact["label"] == "Late"].iloc[0]
    on_time_score = float(on_row["avg_score"])
    late_score = float(late_row["avg_score"])
    gap = on_time_score - late_score

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=["On Time"], y=[on_time_score],
        name="On Time", marker_color=BLUE[1],
        text=[f"<b>{on_time_score:.1f}</b>"],
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(color="white", size=16),
    ))
    fig.add_trace(go.Bar(
        x=["Late"], y=[late_score],
        name="Late", marker_color=BLUE[4],
        text=[f"<b>{late_score:.1f}</b>"],
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(color="white", size=16),
    ))
    style_fig(fig, "")
    fig.update_layout(
        showlegend=True,
        legend_title_text="Submission Status",
        legend=dict(orientation="v", y=1, x=1.02),
        xaxis_title="", yaxis_title="Average Score",
        yaxis_range=[0, max(on_time_score, late_score) * 1.25],
        annotations=[dict(
            text=f"<b>On-time submissions score {gap:.1f} points higher on average</b>",
            x=0.5, y=1.05, xref="paper", yref="paper", showarrow=False,
            font=dict(size=12),
        )],
    )
    return fig
# =====================================================
# Q9 — Attendance Trend Over Time (bar)
# =====================================================
def chart_q9_attendance_trend(monthly: pd.DataFrame) -> go.Figure:
    df = monthly.copy()
    df["month"] = _month_label(df["month"])
    df = df.sort_values("month").reset_index(drop=True)
    month_order = df["month"].tolist()
    avg = df["attendance_rate"].mean()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=month_order, y=df["attendance_rate"].tolist(),
        marker_color=BLUE[3],
        text=[f"<b>{v:.1f}%</b>" for v in df["attendance_rate"]],
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(color="white", size=14),
        name="Attendance",
        showlegend=False,
    ))
    fig.add_hline(y=avg, line_dash="dash",
                  line_color=ACCENT_RED, line_width=2.5)
    fig.add_annotation(
        text=f"<b>Mean: {avg:.1f}%</b>",
        x=1, xref="paper", y=avg, yref="y",
        xanchor="right", yanchor="bottom", showarrow=False,
        bgcolor="rgba(255,255,255,0.95)",
        bordercolor=ACCENT_RED, borderwidth=1, borderpad=4,
        font=dict(size=11, color=ACCENT_RED),
    )
    fig.update_layout(
        title=dict(text=""),
        xaxis=dict(type="category", categoryorder="array",
                   categoryarray=month_order),
        xaxis_title="Month", yaxis_title="Attendance Rate (%)",
        yaxis_range=[0, 100], height=450,
        plot_bgcolor="#fafbfd", paper_bgcolor="white",
        font=dict(family="Segoe UI", size=12, color="#333"),
    )
    fig.update_xaxes(gridcolor="#e8e8e8")
    fig.update_yaxes(gridcolor="#e8e8e8")
    return fig
# =====================================================
# Q9 — Platform Activities per Student (line)
# =====================================================
def chart_q9_engagement_trend(monthly: pd.DataFrame) -> go.Figure:
    df = monthly.copy()
    df["month"] = _month_label(df["month"])
    df = df.sort_values("month").reset_index(drop=True)

    month_order = df["month"].tolist()           # exact labels, in order
    avg = df["events_per_student"].mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=month_order,                            # pass the list, not the Series
        y=df["events_per_student"].tolist(),
        mode="lines+markers+text",
        line=dict(width=4, color=BLUE[2]),
        marker=dict(size=12, color=BLUE[2]),
        text=df["events_per_student"].round(1).tolist(),
        textposition="top center",
        name="Platform Activities",
    ))
    fig.add_hline(
        y=avg, line_dash="dash", line_color=ACCENT_RED,
        annotation_text=f"Average ({avg:.1f})",
    )
    fig.update_layout(
        title="Platform Activities per Student",
        xaxis=dict(
            type="category",
            categoryorder="array",
            categoryarray=month_order,
        ),
        xaxis_title="Month", yaxis_title="Activities per Student",
        showlegend=False, height=450,
        plot_bgcolor="#fafbfd", paper_bgcolor="white",
        font=dict(family="Segoe UI", size=12, color="#333"),
    )
    fig.update_xaxes(gridcolor="#e8e8e8")
    fig.update_yaxes(gridcolor="#e8e8e8")
    return fig
# =====================================================
# Q10 — Grade & Attendance by Age Band
# =====================================================
def chart_q10_age_bands(master: pd.DataFrame) -> go.Figure:
    df = add_age_band(master)
    agg = (
        df.groupby("age_band", observed=True)
          .agg(avg_grade=("avg_grade", "mean"),
               attendance=("attendance_rate", lambda x: (x * 100).mean()),
               count=("student_id", "count"))
          .reset_index()
    )

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=agg["age_band"], y=agg["avg_grade"],
        name="Avg Grade", marker_color=BLUE[1],
    ))
    fig.add_trace(go.Bar(
        x=agg["age_band"], y=agg["attendance"],
        name="Attendance %", marker_color=BLUE[3],
    ))
    fig.update_layout(barmode="group")
    style_fig(fig, "Q10: Grade & Attendance by Age Band")
    fig.update_layout(xaxis_title="Age Band", yaxis_title="Value")
    return fig


# =====================================================
# Q11 Extension — Risk Concentration by Group
# =====================================================
def chart_risk_concentration_by_group(master: pd.DataFrame) -> go.Figure:
    """Count of 'Needs Attention' (cluster==1) students per group.

    Mirrors the notebook's `risk_by_group` chart. The largest contributor
    is highlighted in the deepest BLUE so the concentration is immediate.
    """
    if master is None or master.empty:
        fig = go.Figure()
        style_fig(fig, "Q11 Extension — Risk Concentration by Group")
        fig.add_annotation(text="No data for the current selection.",
                           xref="paper", yref="paper", x=0.5, y=0.5,
                           showarrow=False, font=dict(color="#64748B"))
        return fig

    # Filter to Needs Attention. Use 'cluster'==1 if present (notebook
    # convention), else fall back to a string match on 'segment'.
    if "cluster" in master.columns:
        risk_df = master[master["cluster"] == 1]
    elif "segment" in master.columns:
        risk_df = master[
            master["segment"].astype(str).str.contains("Needs Attention", na=False)
        ]
    else:
        risk_df = master.iloc[0:0]

    if risk_df.empty or "group_name" not in risk_df.columns:
        fig = go.Figure()
        style_fig(fig, "Q11 Extension — Risk Concentration by Group")
        fig.add_annotation(text="No at-risk students in the current selection.",
                           xref="paper", yref="paper", x=0.5, y=0.5,
                           showarrow=False, font=dict(color="#64748B"))
        return fig

    risk_by_group = (
        risk_df.groupby("group_name")
               .size()
               .reset_index(name="At_Risk_Students")
               .sort_values("At_Risk_Students", ascending=True)
    )
    top_group = risk_by_group.iloc[-1]["group_name"]

    colors = [BLUE[0] if g == top_group else BLUE[4]
              for g in risk_by_group["group_name"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=risk_by_group["At_Risk_Students"],
        y=risk_by_group["group_name"],
        orientation="h",
        text=risk_by_group["At_Risk_Students"],
        textposition="outside",
        marker_color=colors,
    ))
    style_fig(fig, "Q11 Extension — Risk Concentration by Group")
    fig.update_layout(
        height=500,
        xaxis_title="Number of At-Risk Students",
        yaxis_title="Group",
        showlegend=False,
        xaxis_range=[0, risk_by_group["At_Risk_Students"].max() * 1.18],
    )
    return fig


# =====================================================
# Q11 — Student Segment Profiles (subplots)
# =====================================================
def chart_q11_segments(cluster_profiles: pd.DataFrame) -> go.Figure:
    df = cluster_profiles.copy()
    df["attendance_rate"] = (df["attendance_rate"] * 100).round(0)
    df["num_failed_concepts"] = df["num_failed_concepts"].round(0)

    features = ["attendance_rate", "avg_grade", "total_events", "num_failed_concepts"]
    labels = ["Attendance %", "Avg Grade", "Total Events", "Failed Concepts"]
    names = {0: "⭐ High Achievers", 1: "⚠️ Needs Attention", 2: "📊 Average Performers"}

    df = df.sort_values("cluster").reset_index(drop=True)

    fig = make_subplots(
        rows=1, cols=len(df), shared_yaxes=True,
        subplot_titles=[
            f"{names.get(int(c), f'Segment {c}')} ({int(s)} students)"
            for c, s in zip(df["cluster"], df["students"])
        ],
    )

    for i, (_, row) in enumerate(df.iterrows()):
        vals = [row[f] for f in features]
        fig.add_trace(go.Bar(
            x=labels, y=vals, marker_color=BLUE[i % len(BLUE)],
            text=[int(v) for v in vals],
            textposition="outside",
            textfont=dict(size=14),
            showlegend=False,
        ), row=1, col=i + 1)

    style_fig(fig, "Q11: Student Segments — Feature Profiles")
    fig.update_layout(height=450)
    return fig


# =====================================================
# Q12 — Stated vs Actual Group Sizes
# =====================================================
def chart_q12_group_sizes(sizes: pd.DataFrame) -> go.Figure:
    df = sizes.sort_values("gap", ascending=False)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Stated", x=df["group_name"],
        y=df["stated_num_students"], marker_color=BLUE[4],
    ))
    fig.add_trace(go.Bar(
        name="Actual", x=df["group_name"],
        y=df["true_count"], marker_color=BLUE[1],
    ))
    fig.update_layout(barmode="group")
    style_fig(fig, "Q12: Stated vs Actual Group Sizes")
    fig.update_layout(
        xaxis_title="", yaxis_title="Students",
        xaxis_tickangle=-45,
    )
    return fig


# =====================================================
# Q13 — G10 Student vs Closest Match (concept profile)
# =====================================================
def chart_q13_merge_comparison(rec: dict) -> go.Figure:
    cmp = rec.get("concept_comparison", [])
    concepts = [c["concept"][:20] for c in cmp]
    g10_scores = [c["g10_score"] for c in cmp]
    match_scores = [c["match_score"] for c in cmp]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=concepts, y=g10_scores,
        name=f"{rec.get('non_viable_student_name','G10 student')} (G10)",
        marker_color=BLUE[1],
        text=[f"{v:.0f}" for v in g10_scores],
        textposition="outside",
    ))
    fig.add_trace(go.Bar(
        x=concepts, y=match_scores,
        name=f"{rec.get('matched_student_name','Match')} ({rec.get('recommended_target_group_id','')})",
        marker_color=BLUE[4],
        text=[f"{v:.0f}" for v in match_scores],
        textposition="outside",
    ))
    fig.update_layout(barmode="group")
    style_fig(fig, "Q13: G10 Student vs Closest Match — Concept Profile")
    fig.update_layout(
        xaxis_title="", yaxis_title="Score %",
        xaxis_tickangle=-30,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="center", x=0.5),
    )
    return fig


# =====================================================
# Q14 — Top 10 At-Risk Students
# =====================================================
def chart_q14_top_at_risk(at_risk_df: pd.DataFrame) -> go.Figure:
    df = at_risk_df.copy()
    # at_risk.csv saved without risk_score column; if absent, derive an ordering.
    if "risk_score" not in df.columns:
        df["risk_score"] = (
            (1 - df["attendance_rate"]) * 0.25
            + (1 - df["avg_grade"] / df["avg_grade"].max()) * 0.30
            + df["num_failed_concepts"] / df["num_failed_concepts"].max() * 0.25
        ).round(3)
    df = df.sort_values("risk_score", ascending=False).head(10)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df["full_name"], x=df["risk_score"],
        orientation="h", marker_color=BLUE[1],
        text=df["risk_score"], textposition="outside",
    ))
    style_fig(fig, "Q14: Top 10 At-Risk Students")
    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        xaxis_title="Risk Score (higher = more urgent)",
        yaxis_title="", showlegend=False,
    )
    return fig


# =====================================================
# Q14 — At-Risk Course Concentration
# =====================================================
def chart_q14_course_concentration(at_risk_df: pd.DataFrame) -> go.Figure:
    counts = at_risk_df["course_name"].value_counts().reset_index()
    counts.columns = ["course_name", "at_risk_count"]
    top_course = counts.iloc[0]["course_name"]
    top_count = int(counts.iloc[0]["at_risk_count"])

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=counts["course_name"], y=counts["at_risk_count"],
        marker_color=[BLUE[0] if c == top_course else BLUE[4]
                      for c in counts["course_name"]],
        text=counts["at_risk_count"], textposition="outside",
        textfont=dict(size=18),
    ))
    style_fig(fig, "Q14: At-Risk Students Are Concentrated in One Course")
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Number of At-Risk Students (Top 10)",
        yaxis_range=[0, counts["at_risk_count"].max() * 1.3],
        showlegend=False,
        annotations=[dict(
            text=f"{top_count} out of {int(counts['at_risk_count'].sum())} at-risk students belong to {top_course}",
            x=0.5, y=1.08, xref="paper", yref="paper",
            showarrow=False, font=dict(size=14, color=BLUE[0]),
        )],
    )
    return fig


# =====================================================
# Q15 — Group Performance Trend (slopes)
# =====================================================
def chart_q15_grade_trends(trends: pd.DataFrame) -> go.Figure:
    df = trends[trends["Group"] != "G10"].sort_values("Slope").reset_index(drop=True)

    point_colors = [
        "#d62728" if s <= -0.35 else
        "#2ca02c" if s > 0 else
        "#94a3b8"
        for s in df["Slope"]
    ]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Group"], y=df["Slope"],
        mode="lines+markers+text",
        line=dict(color=BLUE[3], width=3, shape="spline"),
        marker=dict(size=18, color=point_colors,
                    line=dict(color="white", width=2.5)),
        text=[f"<b>{s:+.2f}</b>" for s in df["Slope"]],
        textposition="top center",
        textfont=dict(size=11),
        hovertemplate="<b>%{x}</b><br>Slope: %{y:+.2f} pts/month<extra></extra>",
        showlegend=False,
    ))
    fig.add_hline(y=0, line_dash="dash", line_color="#0F172A", line_width=2)

    # color legend via dummy traces
    fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers",
        marker=dict(size=14, color="#d62728"),
        name="Sharp decline (≤ -0.35)"))
    fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers",
        marker=dict(size=14, color="#94a3b8"),
        name="Mild decline"))
    fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers",
        marker=dict(size=14, color="#2ca02c"),
        name="Improving (> 0)"))

    fig.update_layout(
        title=dict(text=""),
        xaxis_title="Group (sorted by trajectory — worst to best)",
        yaxis_title="Monthly Grade Change (Points per Month)",
        height=500,
        plot_bgcolor="#fafbfd",
        paper_bgcolor="white",
        font=dict(family="Segoe UI", size=12, color="#333"),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.25,
                    xanchor="center", x=0.5),
        margin=dict(l=60, r=30, t=30, b=80),
    )
    fig.update_xaxes(gridcolor="#e8e8e8")
    fig.update_yaxes(gridcolor="#e8e8e8")
    return fig
