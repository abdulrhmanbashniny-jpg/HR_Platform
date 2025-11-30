import streamlit as st
import supabase
from datetime import datetime
from config import SUPABASE_URL, SUPABASE_KEY, APP_TITLE, APP_ICON, APP_VERSION, EMPLOYEES, REQUEST_TYPES

# إعداد صفحة Streamlit
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ثيم عربي بسيط
st.markdown("""
<style>
    .main { direction: rtl; text-align: right; }
    .stButton > button { width: 100%; }
</style>
""", unsafe_allow_html=True)

# اتصال Supabase
@st.cache_resource
def get_client():
    return supabase.create_client(SUPABASE_URL, SUPABASE_KEY)

client = get_client()

def login_page():
    st.title("🔐 تسجيل الدخول")
    emp_id = st.text_input("رقم الموظف", placeholder="مثال: 001")
    if st.button("دخول"):
        if emp_id in EMPLOYEES:
            st.session_state.logged_in = True
            st.session_state.emp_id = emp_id
            st.rerun()
        else:
            st.error("رقم الموظف غير صحيح")

def dashboard_page():
    emp_id = st.session_state.emp_id
    emp = EMPLOYEES[emp_id]
    st.title("📊 لوحة التحكم")
    st.write(f"مرحباً، {emp['name']}")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("القسم", emp["department"])
    with col2:
        st.metric("الدور", emp["role"])
    with col3:
        st.metric("الإصدار", APP_VERSION)

    st.divider()
    st.subheader("القائمة الرئيسية")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("➕ طلب جديد"):
            st.session_state.page = "new_request"
            st.rerun()
    with c2:
        if st.button("📝 طلباتي"):
            st.session_state.page = "my_requests"
            st.rerun()
    with c3:
        if st.button("✅ الموافقات"):
            st.session_state.page = "approvals"
            st.rerun()

def new_request_page():
    st.title("➕ إنشاء طلب جديد")
    with st.form("new_req"):
        req_type_key = st.selectbox(
            "نوع الطلب",
            list(REQUEST_TYPES.keys()),
            format_func=lambda k: REQUEST_TYPES[k]["name"]
        )
        subtype = st.selectbox("النوع الفرعي", REQUEST_TYPES[req_type_key]["subtypes"])
        title = st.text_input("عنوان الطلب")
        desc = st.text_area("وصف الطلب")
        start = st.date_input("تاريخ البداية")
        end = st.date_input("تاريخ النهاية")

        submitted = st.form_submit_button("📤 إرسال")
        if submitted:
            req_id = f"REQ-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            data = {
                "request_id": req_id,
                "employee_id": st.session_state.emp_id,
                "request_type": req_type_key,
                "request_subtype": subtype,
                "title": title,
                "description": desc,
                "start_date": str(start),
                "end_date": str(end),
                "status": "pending",
            }
            client.table("requests").insert(data).execute()
            st.success(f"تم إرسال الطلب بنجاح، رقم الطلب: {req_id}")

def my_requests_page():
    st.title("📝 طلباتي")
    emp_id = st.session_state.emp_id
    res = client.table("requests").select("*").eq("employee_id", emp_id).order("created_at", desc=True).execute()
    rows = res.data or []
    if not rows:
        st.info("لا توجد طلبات حتى الآن.")
        return
    st.dataframe(rows)

def approvals_page():
    st.title("✅ الموافقات")
    st.info("هذه الصفحة ستُطوّر لاحقاً لمسار الموافقات الهرمي.")

def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "page" not in st.session_state:
        st.session_state.page = "dashboard"

    # الشريط الجانبي
    with st.sidebar:
        st.title(APP_TITLE)
        st.write(f"الإصدار: {APP_VERSION}")
        st.divider()
        if st.session_state.logged_in:
            emp = EMPLOYEES[st.session_state.emp_id]
            st.write(f"👤 {emp['name']}")
            st.write(f"🏢 {emp['department']}")
            st.divider()
            if st.button("🚪 تسجيل خروج"):
                st.session_state.clear()
                st.rerun()

    if not st.session_state.logged_in:
        login_page()
    else:
        if st.session_state.page == "dashboard":
            dashboard_page()
        elif st.session_state.page == "new_request":
            new_request_page()
        elif st.session_state.page == "my_requests":
            my_requests_page()
        elif st.session_state.page == "approvals":
            approvals_page()

if __name__ == "__main__":
    main()
