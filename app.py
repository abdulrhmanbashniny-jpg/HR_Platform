import streamlit as st
from datetime import datetime
from config import APP_TITLE, APP_ICON, APP_VERSION, EMPLOYEES, REQUEST_TYPES

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")

if "requests" not in st.session_state:
    st.session_state["requests"] = []

def save_request_local(data: dict):
    st.session_state["requests"].append(data)

def get_requests_local(emp_id: str):
    return [r for r in st.session_state["requests"] if r["employee_id"] == emp_id]
