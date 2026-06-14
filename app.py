"""Kayfa Student Analytics — Streamlit entry point."""
import streamlit as st

from config import APP_NAME, FAVICON_PATH
from components.injector import inject_styles
from auth import require_auth, is_authenticated


st.set_page_config(
    page_title=APP_NAME,
    page_icon=str(FAVICON_PATH),
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_styles()

# Login gate
require_auth()

# Once authenticated, send the user to Overview
if is_authenticated():
    try:
        st.switch_page("pages/1_📊_Overview.py")
    except Exception:
        # fall back: render a tiny landing if switch_page isn't supported
        st.title("Welcome to Kayfa Student Analytics")
        st.markdown("Use the sidebar to navigate to a page.")
