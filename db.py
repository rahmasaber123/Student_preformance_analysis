"""Mongo connection — cached across reruns."""
import os
import streamlit as st
from pymongo import MongoClient
from dotenv import load_dotenv

from config import MONGO_DB_NAME

load_dotenv()


def _get_uri() -> str:
    # Prefer Streamlit secrets (cloud), fallback to .env (local)
    try:
        return st.secrets["MONGO_URI"]
    except Exception:
        uri = os.getenv("MONGO_URI")
        if not uri:
            st.error(
                "MONGO_URI not configured. Set it in `.env` (local) "
                "or `.streamlit/secrets.toml` (deploy)."
            )
            st.stop()
        return uri


@st.cache_resource(show_spinner=False)
def get_client() -> MongoClient:
    return MongoClient(_get_uri(), serverSelectionTimeoutMS=8000)


def get_db():
    return get_client()[MONGO_DB_NAME]
