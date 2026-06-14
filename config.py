"""Kayfa Dashboard — app-wide config."""
from pathlib import Path

APP_NAME = "Kayfa Student Analytics"
APP_TAGLINE = "Data • Insights • Intervention"

ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"
LOGO_PATH = ASSETS / "kayfa_logo.png"
FAVICON_PATH = ASSETS / "favicon.ico"
CSS_PATH = ASSETS / "styles.css"

# Mongo
MONGO_DB_NAME = "kayfa_analytics"

# --- Brand palette (UI shell) ---
COLORS = {
    "navy_900": "#0F172A",
    "navy_800": "#1E293B",
    "navy_700": "#334155",
    "blue_600": "#2563EB",
    "blue_500": "#3B82F6",
    "blue_400": "#60A5FA",
    "bg":       "#F8FAFC",
    "card":     "#FFFFFF",
    "success":  "#10B981",
    "warning":  "#F59E0B",
    "danger":   "#EF4444",
    "text":     "#0F172A",
    "muted":    "#64748B",
}

# --- Chart palette (matches the notebook's BLUE) ---
# BLUE = ['#08306b','#08519c','#2171b5','#4292c6','#6baed6','#9ecae1','#c6dbef','#deebf7']
BLUE = [
    "#08306b", "#08519c", "#2171b5", "#4292c6",
    "#6baed6", "#9ecae1", "#c6dbef", "#deebf7",
]
CHART_BG = "#fafbfd"
ACCENT_RED = "#e63946"
