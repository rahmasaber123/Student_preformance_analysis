"""High-level query functions — one per Atlas collection.

These wrap `mongo.fetch_collection` / `fetch_one` so pages stay clean.
"""
from utils.mongo import fetch_collection, fetch_one


# ---------- Overview ----------
def kpi_overview():
    return fetch_one("kpi_overview")


def monthly_attendance():
    return fetch_collection("monthly_attendance", sort=[("month", 1)])


def monthly_engagement():
    return fetch_collection("monthly_engagement", sort=[("month", 1)])


# ---------- Groups ----------
def group_attendance():
    return fetch_collection("group_attendance")


def group_sizes():
    return fetch_collection("group_sizes")


def grade_trends():
    return fetch_collection("grade_trends")


def group_merge_recommendation():
    return fetch_one("group_merge_recommendation")


# ---------- Performance ----------
def course_stats():
    return fetch_collection("course_stats")


def type_stats():
    return fetch_collection("type_stats")


def late_submission_impact():
    return fetch_collection("late_submission_impact")


# ---------- Concepts ----------
def concept_failures():
    return fetch_collection("concept_failures")


def concept_mastery_timeline():
    return fetch_collection("concept_mastery_timeline", sort=[("month", 1)])


# ---------- At-Risk / Segments ----------
def at_risk():
    return fetch_collection("at_risk")


def cluster_profiles():
    return fetch_collection("cluster_profiles")


def student_segments():
    return fetch_collection("student_segments")


# ---------- Master (student-level) ----------
def master():
    return fetch_collection("master")


def filter_options():
    return fetch_one("filter_options")
