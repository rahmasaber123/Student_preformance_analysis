"""Authentication: bcrypt password check against the `users` collection."""
import base64
from pathlib import Path

import bcrypt
import streamlit as st

from db import get_db
from config import APP_NAME, APP_TAGLINE, LOGO_PATH


def _verify(username: str, password: str) -> dict | None:
    """Return the user doc if credentials are valid, else None."""
    db = get_db()
    user = db.users.find_one({"username": username}, {"_id": 0})
    if not user:
        return None
    hashed = user.get("password_hash", "").encode()
    try:
        if bcrypt.checkpw(password.encode(), hashed):
            return user
    except Exception:
        return None
    return None


def is_authenticated() -> bool:
    return bool(st.session_state.get("authenticated"))


def _logo_b64() -> str:
    return base64.b64encode(Path(LOGO_PATH).read_bytes()).decode()


def render_login_page() -> None:
    """The centered login layout from the user's spec."""
    # hide the sidebar while not logged in
    st.markdown(
        '<style>section[data-testid="stSidebar"]{display:none!important;}'
        '[data-testid="collapsedControl"]{display:none!important;}</style>',
        unsafe_allow_html=True,
    )

    logo = _logo_b64()
    st.markdown(
        f"""
        <div class="kf-login-wrap">
          <img class="kf-login-logo" src="data:image/png;base64,{logo}" alt="Kayfa"/>
          <div class="kf-login-title">{APP_NAME}</div>
          <div class="kf-login-tag">{APP_TAGLINE}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _, mid, _ = st.columns([1, 1.2, 1])
    with mid:
        username = st.text_input("Username", placeholder="Username",
                                 label_visibility="collapsed")
        password = st.text_input("Password", placeholder="Password",
                                 type="password", label_visibility="collapsed")

        if st.button("Sign In", use_container_width=True, type="primary"):
            if not username or not password:
                st.warning("Enter a username and password.")
                return
            user = _verify(username, password)
            if user:
                st.session_state["authenticated"] = True
                st.session_state["username"] = user["username"]
                st.session_state["user_name"] = user.get("name") or user["username"]
                st.rerun()
            else:
                st.error("Invalid username or password.")


def require_auth() -> None:
    """Call at the top of every page (incl. app.py).

    If not authenticated → show login UI and stop the page.
    """
    if not is_authenticated():
        render_login_page()
        st.stop()
