"""Sidebar — global filters + user info + logout.

v2: more filters (Gender, Segment, Instructor) that genuinely filter aggregate
collections by joining through the master collection on student / group / course
identifiers.
"""
import base64
from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st

from config import LOGO_PATH
from utils.queries import filter_options, master


def _logo_b64() -> str:
    return base64.b64encode(Path(LOGO_PATH).read_bytes()).decode()


def _ensure_state_defaults() -> None:
    for key in ("filter_groups", "filter_courses", "filter_age_bands",
                "filter_genders", "filter_segments", "filter_instructors"):
        st.session_state.setdefault(key, [])


@st.cache_data(ttl=600, show_spinner=False)
def _extra_options_from_master() -> dict:
    """Derive Gender / Segment / Instructor options from the master collection."""
    df = master()
    if df.empty:
        return {"genders": [], "segments": [], "instructors": []}
    out = {}
    for col, key in [("gender", "genders"),
                     ("segment", "segments"),
                     ("instructor", "instructors")]:
        if col in df.columns:
            out[key] = sorted(df[col].dropna().unique().tolist())
        else:
            out[key] = []
    return out


def render_sidebar(active: str = "") -> dict:
    """Render the sidebar; return the active filter selections."""
    _ensure_state_defaults()
    opts = filter_options() or {}
    extra = _extra_options_from_master()

    with st.sidebar:
        # Brand
        logo = _logo_b64()
        st.markdown(
            f"""
            <div class="kf-sidebar-brand">
              <img src="data:image/png;base64,{logo}" alt="Kayfa"/>
              <div class="kf-sidebar-brand-text">
                <div class="kf-sidebar-brand-name">Kayfa</div>
                <div class="kf-sidebar-brand-sub">Student Analytics</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="kf-sidebar-section">FILTERS</div>',
                    unsafe_allow_html=True)

        groups = st.multiselect(
            "Group",
            options=opts.get("group_ids", []),
            key="filter_groups",
            placeholder="All groups",
        )
        courses = st.multiselect(
            "Course",
            options=opts.get("course_ids", []),
            key="filter_courses",
            placeholder="All courses",
        )
        age_bands = st.multiselect(
            "Age band",
            options=opts.get("age_bands", []),
            key="filter_age_bands",
            placeholder="All ages",
        )

        with st.expander("More filters", expanded=False):
            genders = st.multiselect(
                "Gender",
                options=extra.get("genders", []),
                key="filter_genders",
                placeholder="All",
            )
            segments = st.multiselect(
                "Segment",
                options=extra.get("segments", []),
                key="filter_segments",
                placeholder="All segments",
            )
            instructors = st.multiselect(
                "Instructor",
                options=extra.get("instructors", []),
                key="filter_instructors",
                placeholder="All instructors",
            )

        if st.button("Reset filters", use_container_width=True):
            for k in ("filter_groups", "filter_courses", "filter_age_bands",
                      "filter_genders", "filter_segments", "filter_instructors"):
                st.session_state[k] = []
            st.rerun()

        st.markdown('<div class="kf-sidebar-spacer"></div>',
                    unsafe_allow_html=True)

        # User block
        user = st.session_state.get("user_name", "Kayfa Admin")
        st.markdown(
            f"""
            <div class="kf-sidebar-user">
              <div class="kf-sidebar-user-avatar">{user[:1].upper()}</div>
              <div class="kf-sidebar-user-meta">
                <div class="kf-sidebar-user-name">{user}</div>
                <div class="kf-sidebar-user-role">Administrator</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Log out", use_container_width=True, key="logout_btn"):
            for k in ("authenticated", "username", "user_name"):
                st.session_state.pop(k, None)
            st.rerun()

    return {
        "groups": groups,
        "courses": courses,
        "age_bands": age_bands,
        "genders": genders,
        "segments": segments,
        "instructors": instructors,
    }


# ============================================================
# Filter helpers
# ============================================================

def is_any_filter_active(filters: dict) -> bool:
    return any(filters.get(k) for k in ("groups", "courses", "age_bands",
                                        "genders", "segments", "instructors"))


def render_active_filter_chips(filters: dict) -> None:
    """Render a small pill row showing which filters are active."""
    if not is_any_filter_active(filters):
        return
    chips = []
    for label, key in [("Group", "groups"), ("Course", "courses"),
                       ("Age", "age_bands"), ("Gender", "genders"),
                       ("Segment", "segments"), ("Instructor", "instructors")]:
        for v in filters.get(key, []) or []:
            chips.append(f'<span class="kf-filter-pill">{label}: {v}</span>')
    if chips:
        st.markdown(
            f'<div class="kf-active-filters"><strong>Active filters:</strong> '
            f'{" ".join(chips)}</div>',
            unsafe_allow_html=True,
        )


def apply_master_filters(master_df: Optional[pd.DataFrame],
                         filters: dict) -> Optional[pd.DataFrame]:
    """Apply sidebar filters to the master (student-level) DataFrame."""
    if master_df is None or master_df.empty:
        return master_df

    df = master_df.copy()

    if filters.get("groups") and "group_id" in df.columns:
        df = df[df["group_id"].isin(filters["groups"])]
    if filters.get("courses") and "course_id" in df.columns:
        df = df[df["course_id"].isin(filters["courses"])]
    if filters.get("instructors") and "instructor" in df.columns:
        df = df[df["instructor"].isin(filters["instructors"])]
    if filters.get("genders") and "gender" in df.columns:
        df = df[df["gender"].isin(filters["genders"])]
    if filters.get("segments") and "segment" in df.columns:
        df = df[df["segment"].isin(filters["segments"])]
    if filters.get("age_bands"):
        if "age_band" not in df.columns and "age" in df.columns:
            df["age_band"] = pd.cut(
                df["age"],
                bins=[0, 20, 25, 30, 100],
                labels=["<20", "20-25", "26-30", "30+"],
            ).astype(str)
        if "age_band" in df.columns:
            df = df[df["age_band"].astype(str).isin(filters["age_bands"])]
    return df


# ------------------------------------------------------------
# Filtering helpers for the pre-aggregated collections
# ------------------------------------------------------------
@st.cache_data(ttl=600, show_spinner=False)
def _active_student_ids(filters_key: tuple) -> set:
    """Return the student_ids that survive the sidebar filters."""
    filters = dict(filters_key)
    df = master()
    df = apply_master_filters(df, {k: list(v) for k, v in filters.items()})
    if df is None or df.empty or "student_id" not in df.columns:
        return set()
    return set(df["student_id"].astype(str).tolist())


@st.cache_data(ttl=600, show_spinner=False)
def _active_group_ids(filters_key: tuple) -> set:
    filters = dict(filters_key)
    df = master()
    df = apply_master_filters(df, {k: list(v) for k, v in filters.items()})
    if df is None or df.empty or "group_id" not in df.columns:
        return set()
    return set(df["group_id"].astype(str).tolist())


@st.cache_data(ttl=600, show_spinner=False)
def _active_course_ids(filters_key: tuple) -> set:
    filters = dict(filters_key)
    df = master()
    df = apply_master_filters(df, {k: list(v) for k, v in filters.items()})
    if df is None or df.empty or "course_id" not in df.columns:
        return set()
    return set(df["course_id"].astype(str).tolist())


def _filters_key(filters: dict) -> tuple:
    """Hashable key for caching the active-id sets."""
    return tuple(sorted(
        (k, tuple(sorted(v or []))) for k, v in filters.items()
    ))


def filter_by_group(df: pd.DataFrame, filters: dict,
                    group_col: str = "group_id") -> pd.DataFrame:
    """Subset an aggregate frame to the group_ids surviving sidebar filters."""
    if df is None or df.empty or not is_any_filter_active(filters):
        return df
    if group_col not in df.columns:
        return df
    active = _active_group_ids(_filters_key(filters))
    if not active:
        return df.iloc[0:0]   # empty but same schema
    return df[df[group_col].astype(str).isin(active)]


def filter_by_course(df: pd.DataFrame, filters: dict,
                     course_col: str = "course_id") -> pd.DataFrame:
    if df is None or df.empty or not is_any_filter_active(filters):
        return df
    if course_col not in df.columns:
        return df
    active = _active_course_ids(_filters_key(filters))
    if not active:
        return df.iloc[0:0]
    return df[df[course_col].astype(str).isin(active)]


def filter_by_student(df: pd.DataFrame, filters: dict,
                      student_col: str = "student_id") -> pd.DataFrame:
    if df is None or df.empty or not is_any_filter_active(filters):
        return df
    if student_col not in df.columns:
        return df
    active = _active_student_ids(_filters_key(filters))
    if not active:
        return df.iloc[0:0]
    return df[df[student_col].astype(str).isin(active)]