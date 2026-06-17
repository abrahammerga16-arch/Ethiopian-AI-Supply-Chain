"""utils/auth.py"""
import streamlit as st
import hashlib
from utils.db import get_user_by_email, create_user


def _hash(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


def init_session():
    st.session_state.setdefault("logged_in", False)
    st.session_state.setdefault("user", None)


def login_user(email, password):
    if not email or not password:
        return False, "Please enter email and password."
    user = get_user_by_email(email.strip().lower())
    if not user:
        return False, "No account found with that email."
    if user["pw_hash"] != _hash(password):
        return False, "Incorrect password."
    st.session_state["logged_in"] = True
    st.session_state["user"] = user
    return True, "OK"


def register_user(name, email, pw, role, region, phone):
    ok, result = create_user(name, email.strip().lower(), pw, role, region, phone)
    if ok:
        return True, "Account created."
    return False, result


def logout_user():
    st.session_state["logged_in"] = False
    st.session_state["user"] = None
