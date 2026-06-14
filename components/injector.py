"""Inject the stylesheet on every page."""
from pathlib import Path
import streamlit as st

from config import CSS_PATH


def inject_styles() -> None:
    css = Path(CSS_PATH).read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
