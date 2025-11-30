import streamlit as st

st.set_page_config(
    page_title="منصة الموارد البشرية - نسخة تجريبية",
    page_icon="🏢",
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
        if not emp_id:
            st.error("رجاءً أدخل رقم الموظف.")
            return

        st.session_state.logged_in = True
        st.session_state.emp_id = emp_id
        st.rerun()

def dashboard_page():
    st.title("📊 لوحة التحكم (نسخة مبسطة)")
    st.write(f"أهلاً بك، رقم الموظف الحالي: {st.session_state.emp_id}")
    st.info("هذه نسخة تجريبية للتأكد أن التسجيل والتنقل يعملان بشكل صحيح.")

    if st.button("🚪 تسجيل خروج"):
        st.session_state.clear()
        st.rerun()

def main():
    if not st.session_state.logged_in:
        login_page()
    else:
        dashboard_page()

if __name__ == "__main__":
    main()
