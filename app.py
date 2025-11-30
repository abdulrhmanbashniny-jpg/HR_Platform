import streamlit as st
from config import APP_TITLE, APP_ICON, APP_VERSION, EMPLOYEES

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "emp_id" not in st.session_state:
    st.session_state.emp_id = None

def login_page():
    st.title("🔐 تسجيل الدخول")

    emp_id = st.text_input("رقم الموظف", placeholder="مثال: 001")

    if st.button("دخول"):
        emp_id = emp_id.strip()
        if emp_id in EMPLOYEES:
            st.session_state.logged_in = True
            st.session_state.emp_id = emp_id
            st.rerun()
        else:
            st.error("رقم الموظف غير موجود في النظام (جرّب 001 إلى 005).")

def dashboard_page():
    emp_id = st.session_state.emp_id
    emp = EMPLOYEES[emp_id]

    st.title("📊 لوحة التحكم (مرتبطة بالموظف)")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("الموظف", emp["name"])
    with c2:
        st.metric("القسم", emp["department"])
    with c3:
        st.metric("الدور", emp["role"])
    with c4:
        st.metric("إصدار النظام", APP_VERSION)

    st.divider()
    st.info("هذا عرض مبسط لملف الموظف. لاحقاً نضيف الطلبات، الإجازات، وغيرها.")

    if st.button("🚪 تسجيل خروج"):
        st.session_state.clear()
        st.rerun()

def main():
    with st.sidebar:
        st.title(APP_TITLE)
        st.write(f"الإصدار: {APP_VERSION}")
        st.divider()
        if st.session_state.logged_in:
            emp = EMPLOYEES[st.session_state.emp_id]
            st.write(f"👤 {emp['name']}")
            st.write(f"🏢 {emp['department']}")

    if not st.session_state.logged_in:
        login_page()
    else:
        dashboard_page()

if __name__ == "__main__":
    main()
