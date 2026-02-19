import streamlit as st
import json
import os
from typing import Optional, Dict


def get_users():
    raw = os.getenv("APP_USERS_JSON", "").strip()
    if not raw:
        return [
            {"u": "admin", "p": "admin123", "role": "admin"},
            {"u": "user", "p": "user123", "role": "user"}
        ]
    try:
        return json.loads(raw)
    except Exception:
        return []


def authenticate(username: str, password: str) -> Optional[Dict]:
    for rec in get_users():
        if rec["u"] == username and rec["p"] == password:
            return {"username": username, "role": rec.get("role", "user")}
    return None


def is_authed() -> bool:
    return st.session_state.get("auth", {}).get("is_auth", False)


def get_current_user() -> Optional[Dict]:
    if is_authed():
        return st.session_state["auth"].get("user")
    return None


def require_auth():
    if not is_authed():
        st.switch_page("Login.py")


def logout():
    st.session_state.clear()
    st.switch_page("Login.py")