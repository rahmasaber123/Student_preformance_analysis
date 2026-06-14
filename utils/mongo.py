"""Generic Mongo fetch helpers with Streamlit caching."""
from typing import Optional, Dict, Any, List
import pandas as pd
import streamlit as st

from db import get_db


@st.cache_data(ttl=600, show_spinner=False)
def fetch_collection(
    name: str,
    projection: Optional[Dict[str, int]] = None,
    sort: Optional[List[tuple]] = None,
    query: Optional[Dict[str, Any]] = None,
) -> pd.DataFrame:
    """Load a Mongo collection as a DataFrame (cached 10 min)."""
    db = get_db()
    proj = projection or {"_id": 0}
    cursor = db[name].find(query or {}, proj)
    if sort:
        cursor = cursor.sort(sort)
    docs = list(cursor)
    return pd.DataFrame(docs) if docs else pd.DataFrame()


@st.cache_data(ttl=600, show_spinner=False)
def fetch_one(name: str, query: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Load a single document (cached)."""
    db = get_db()
    doc = db[name].find_one(query or {}, {"_id": 0})
    return doc or {}
