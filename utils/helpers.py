"""Chart styling — mirrors the notebook's `style_fig` to keep charts identical."""
import pandas as pd
import plotly.graph_objects as go

from config import BLUE, CHART_BG, ACCENT_RED  # noqa: F401  (re-exported)


def style_fig(fig: go.Figure, title: str = "") -> go.Figure:
    """Apply consistent chart styling. Section headers carry the title now."""
    fig.update_layout(
        plot_bgcolor=CHART_BG,
        paper_bgcolor="white",
        font=dict(family="Segoe UI", size=12, color="#333"),
        margin=dict(l=60, r=30, t=30, b=50),
        showlegend=True,
        title=dict(text=""),   # explicit empty — kills "undefined"
    )
    fig.update_xaxes(gridcolor="#e8e8e8")
    fig.update_yaxes(gridcolor="#e8e8e8")
    return fig


# ---------- bucketing helpers (the notebook computed these on the fly) ----------

def add_attendance_band(df: pd.DataFrame, col: str = "attendance_rate") -> pd.DataFrame:
    df = df.copy()
    df["att_band"] = pd.cut(
        df[col],
        bins=[0, 0.4, 0.6, 0.8, 1],
        labels=["<40%", "40-60%", "60-80%", "80-100%"],
    )
    return df


def add_engagement_quartile(df: pd.DataFrame, col: str = "total_events") -> pd.DataFrame:
    df = df.copy()
    df["eng_quartile"] = pd.qcut(
        df[col],
        q=4,
        labels=["Low", "Below Avg", "Above Avg", "High"],
        duplicates="drop",
    )
    return df


def add_age_band(df: pd.DataFrame, col: str = "age") -> pd.DataFrame:
    df = df.copy()
    df["age_band"] = pd.cut(
        df[col],
        bins=[0, 20, 25, 30, 100],
        labels=["<20", "20-25", "26-30", "30+"],
    )
    return df
