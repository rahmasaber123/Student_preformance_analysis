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
        text=df["rate"].apply(lambda x: f"{x}%"),
        textposition="outside",
    ))
    fig.add_vline(
        x=platform_avg, line_dash="dash", line_color=ACCENT_RED,
        annotation_text=f"Avg: {platform_avg:.1f}%",
        annotation_position="top right",
    )
    style_fig(fig, "Q1: Attendance Rate by Group")
    fig.update_layout(
        yaxis_title="", xaxis_title="Attendance Rate (%)",
        xaxis_range=[20, 105], showlegend=False,
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
        name="Avg Score",
        text=df["avg_score"].round(1),
        textposition="outside",
        error_x=dict(
            type="data",
            array=df["std"].round(1),
            color=BLUE[0],
        ),
    ))
    fig.add_vline(
        x=overall_avg, line_dash="dash", line_color=ACCENT_RED,
        annotation_text=f"Overall Avg: {overall_avg:.1f}",
    )
    style_fig(fig, "Q2: Average Score by Assessment Type (± Std Dev)")
    fig.update_layout(
        xaxis_title="Average Score", yaxis_title="Assessment Type",
        xaxis_range=[0, 115], showlegend=False,
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
        text=df["mean"].round(1),
        textposition="outside",
    ))
    fig.add_vline(
        x=overall_avg, line_dash="dash", line_color=ACCENT_RED,
        annotation_text=f"Avg: {overall_avg:.1f}",
    )
    style_fig(fig, "Q3: Average Grade by Course")
    fig.update_layout(
        yaxis_title="", xaxis_title="Average Grade",
        xaxis_range=[0, 100], showlegend=False,
    )
    return fig


# =====================================================
# Q3 deep-dive — Average Student Grade by Instructor
# =====================================================
def chart_instructor_grade(master: pd.DataFrame) -> go.Figure:
    """Aggregate student avg_grade by instructor (from the master collection).

    Mirrors the notebook's Q3 deep-dive chart. Sorted ascending so the
    weakest instructor sits at the left.
    """
    if master is None or master.empty or "instructor" not in master.columns:
        fig = go.Figure()
        style_fig(fig, "Average Student Grade by Instructor")
        fig.add_annotation(
            text="No instructor data available for the current selection.",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(color="#64748B", size=13),
        )
        return fig

    agg = (
        master.dropna(subset=["instructor", "avg_grade"])
              .groupby("instructor")["avg_grade"]
              .mean()
              .reset_index()
              .sort_values("avg_grade")
    )
    overall_avg = agg["avg_grade"].mean()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=agg["instructor"], y=agg["avg_grade"],
        marker_color=BLUE[2],
        text=agg["avg_grade"].round(1),
        textposition="outside",
    ))
    fig.add_hline(
        y=overall_avg, line_dash="dash", line_color=ACCENT_RED,
        annotation_text=f"Avg: {overall_avg:.1f}",
    )
    style_fig(fig, "Average Student Grade by Instructor")
    fig.update_layout(
        xaxis_title="Instructor",
        yaxis_title="Average Grade",
        yaxis_range=[0, 100],
        showlegend=False,
        xaxis_tickangle=-25,
    )
    return fig


# =====================================================
# Q4 — Avg Grade by Attendance Band
# =====================================================
def chart_q4_attendance_band(master: pd.DataFrame) -> go.Figure:
    df = add_attendance_band(master)
    agg = (
        df.groupby("att_band", observed=True)
          .agg(avg_grade=("avg_grade", "mean"),
               students=("student_id", "count"))
          .reset_index()
    )

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=agg["att_band"], y=agg["avg_grade"],
        marker_color=BLUE[2],
        text=[f"{g:.1f}<br>n={n}"
              for g, n in zip(agg["avg_grade"], agg["students"])],
        textposition="outside",
    ))
    style_fig(fig, "Q4: Average Grade by Attendance Band")
    fig.update_layout(
        xaxis_title="Attendance Band",
        yaxis_title="Average Grade",
        yaxis_range=[0, agg["avg_grade"].max() * 1.2],
        showlegend=False,
    )
    return fig


# =====================================================
# Q5A — Avg Grade by Engagement Level
# =====================================================
def chart_q5a_engagement_grade(master: pd.DataFrame) -> go.Figure:
    df = add_engagement_quartile(master)
    agg = (
        df.groupby("eng_quartile", observed=True)
          .agg(avg_grade=("avg_grade", "mean"),
               students=("student_id", "count"))
          .reset_index()
    )
    overall_avg = agg["avg_grade"].mean()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=agg["eng_quartile"], y=agg["avg_grade"],
        marker_color=BLUE[2],
        text=[f"{g:.1f}<br>n={n}"
              for g, n in zip(agg["avg_grade"], agg["students"])],
        textposition="outside",
    ))
    fig.add_hline(
        y=overall_avg, line_dash="dash", line_color=ACCENT_RED,
        annotation_text=f"Overall Average ({overall_avg:.1f})",
    )
    style_fig(fig, "Q5A: Average Grade by Engagement Level")
    fig.update_layout(
        xaxis_title="Engagement Level", yaxis_title="Average Grade",
        showlegend=False,
    )
    return fig


# =====================================================
# Q5B — Avg Platform Activity by Engagement Level
# =====================================================
def chart_q5b_engagement_activity(master: pd.DataFrame) -> go.Figure:
    df = add_engagement_quartile(master)
    agg = (
        df.groupby("eng_quartile", observed=True)
          .agg(avg_events=("total_events", "mean"),
               students=("student_id", "count"))
          .reset_index()
    )

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=agg["eng_quartile"], y=agg["avg_events"],
        marker_color=BLUE[4],
        text=[f"{e:.0f} events<br>n={n}"
              for e, n in zip(agg["avg_events"], agg["students"])],
        textposition="outside",
    ))
    style_fig(fig, "Q5B: Average Platform Activity by Engagement Level")
    fig.update_layout(
        xaxis_title="Engagement Level",
        yaxis_title="Average Platform Engagement",
        showlegend=False,
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


def chart_q10_age_grade(master: pd.DataFrame) -> go.Figure:
    agg = _age_band_aggregate(master)
    avg = agg["avg_grade"].mean()
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=agg["age_band"].astype(str), y=agg["avg_grade"],
        marker_color=BLUE[1],
        text=agg["avg_grade"].round(1),
        textposition="outside",
    ))
    fig.add_hline(y=avg, line_dash="dash", line_color=ACCENT_RED,
                  annotation_text=f"Mean: {avg:.1f}")
    style_fig(fig, "Average Grade by Age Band")
    fig.update_layout(xaxis_title="", yaxis_title="Avg Grade",
                      yaxis_range=[0, max(100, agg["avg_grade"].max() * 1.15)],
                      showlegend=False)
    return fig


def chart_q10_age_attendance(master: pd.DataFrame) -> go.Figure:
    agg = _age_band_aggregate(master)
    avg = agg["attendance"].mean()
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=agg["age_band"].astype(str), y=agg["attendance"],
        marker_color=BLUE[3],
        text=agg["attendance"].round(1).astype(str) + "%",
        textposition="outside",
    ))
    fig.add_hline(y=avg, line_dash="dash", line_color=ACCENT_RED,
                  annotation_text=f"Mean: {avg:.1f}%")
    style_fig(fig, "Attendance by Age Band")
    fig.update_layout(xaxis_title="", yaxis_title="Attendance %",
                      yaxis_range=[0, 100], showlegend=False)
    return fig


def chart_q10_age_engagement(master: pd.DataFrame) -> go.Figure:
    agg = _age_band_aggregate(master)
    avg = agg["engagement"].mean()
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=agg["age_band"].astype(str), y=agg["engagement"],
        marker_color=BLUE[4],
        text=agg["engagement"].round(0),
        textposition="outside",
    ))
    fig.add_hline(y=avg, line_dash="dash", line_color=ACCENT_RED,
                  annotation_text=f"Mean: {avg:.0f}")
    style_fig(fig, "Engagement by Age Band")
    fig.update_layout(xaxis_title="", yaxis_title="Avg Events",
                      yaxis_range=[0, agg["engagement"].max() * 1.2],
                      showlegend=False)
    return fig


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
    """Average grade per course for a single instructor.

    Shows the same data the notebook's Q3 deep-dive surfaces, but as a
    horizontal bar so the grade contrast — not the student split — is
    the visible story. (Function name kept for compatibility with the
    Performance page imports.)
    """
    fig = go.Figure()
    if master is None or master.empty or "instructor" not in master.columns:
        style_fig(fig, f"{instructor_name} — Grade by Course")
        fig.add_annotation(text="No instructor data available.",
                           xref="paper", yref="paper", x=0.5, y=0.5,
                           showarrow=False, font=dict(color="#64748B"))
        return fig

    sub = master[master["instructor"] == instructor_name]
    if sub.empty or "course_name" not in sub.columns:
        style_fig(fig, f"{instructor_name} — Grade by Course")
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

    # Red bar for the underperforming course, navy for the rest
    colors = [
        ACCENT_RED if g < 65 else BLUE[1]
        for g in agg["avg_grade"]
    ]

    fig.add_trace(go.Bar(
        y=agg["course_name"],
        x=agg["avg_grade"],
        orientation="h",
        marker_color=colors,
        text=[f"<b>{g:.1f}</b>  ·  {n} students"
              for g, n in zip(agg["avg_grade"], agg["students"])],
        textposition="outside",
        textfont=dict(size=13),
    ))
    fig.add_vline(
        x=platform_avg, line_dash="dash", line_color="#64748B",
        annotation_text=f"His overall avg: {platform_avg:.1f}",
        annotation_position="top right",
    )
    style_fig(fig, f"{instructor_name} — Avg Grade by Course")
    fig.update_layout(
        xaxis_title="Average Grade",
        yaxis_title="",
        xaxis_range=[0, 100],
        showlegend=False,
        margin=dict(l=20, r=80, t=60, b=40),
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
    # `late_impact` has columns: is_late, avg_score, n_submissions, label
    on_row = late_impact[late_impact["label"] == "On Time"].iloc[0]
    late_row = late_impact[late_impact["label"] == "Late"].iloc[0]
    on_time_score = float(on_row["avg_score"])
    late_score = float(late_row["avg_score"])
    gap = on_time_score - late_score

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=["On Time"], y=[on_time_score],
        name="On Time", marker_color=BLUE[1],
        text=[f"{on_time_score:.1f}<br>n={int(on_row['n_submissions'])}"],
        textposition="outside",
    ))
    fig.add_trace(go.Bar(
        x=["Late"], y=[late_score],
        name="Late", marker_color=BLUE[4],
        text=[f"{late_score:.1f}<br>n={int(late_row['n_submissions'])}"],
        textposition="outside",
    ))
    style_fig(fig, "Q8: Students Who Submit On Time Achieve Higher Scores")
    fig.update_layout(
        showlegend=True,
        legend_title_text="Submission Status",
        legend=dict(orientation="v", y=1, x=1.02),
        xaxis_title="", yaxis_title="Average Score",
        yaxis_range=[0, max(on_time_score, late_score) * 1.25],
        annotations=[dict(
            text=f"On-time submissions score {gap:.1f} points higher on average",
            x=0.5, y=1.08, xref="paper", yref="paper", showarrow=False,
        )],
    )
    return fig

# =====================================================
# Q9 — Attendance Trend Over Time (bar)
# =====================================================
def chart_q9_attendance_trend(monthly: pd.DataFrame) -> go.Figure:
    df = monthly.copy()
    df["month"] = _month_label(df["month"])
    df = df.sort_values("month")
    avg = df["attendance_rate"].mean()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["month"], y=df["attendance_rate"],
        marker_color=BLUE[3],
        text=df["attendance_rate"].round(1).astype(str) + "%",
        textposition="outside", name="Attendance",
    ))
    fig.add_hline(
        y=avg, line_dash="dash", line_color=ACCENT_RED,
        annotation_text=f"Average ({avg:.1f}%)",
    )
    fig.update_layout(
        title="Attendance Trend Over Time",
        xaxis=dict(type="category"),
        xaxis_title="Month", yaxis_title="Attendance Rate (%)",
        yaxis_range=[0, 100], showlegend=False, height=450,
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
    df = trends[trends["Group"] != "G10"].sort_values("Slope")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["Slope"], y=df["Group"], orientation="h",
        text=df["Slope"].round(2), textposition="outside",
        marker_color=[
            "#d62728" if x <= -0.35
            else "#2ca02c" if x > 0
            else "#9e9e9e"
            for x in df["Slope"]
        ],
    ))
    fig.add_vline(x=0, line_dash="dash", line_color="black")
    fig.update_layout(
        title="Q15: Group Performance Trend (Excluding Outlier G10)",
        xaxis_title="Monthly Grade Change (Points per Month)",
        yaxis_title="Group",
        showlegend=False, height=500,
        plot_bgcolor="#fafbfd", paper_bgcolor="white",
        font=dict(family="Segoe UI", size=12, color="#333"),
    )
    fig.update_xaxes(gridcolor="#e8e8e8")
    fig.update_yaxes(gridcolor="#e8e8e8")
    return fig
