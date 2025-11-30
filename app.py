import streamlit as st
from datetime import datetime, date
from config import APP_TITLE, APP_ICON, APP_VERSION, EMPLOYEES, REQUEST_TYPES

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

# تهيئة الجلسة
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "dashboard"

if "requests" not in st.session_state:
    st.session_state.requests = []  # قائمة الطلبات في الذاكرة فقط

# دوال مساعدة محلية (بدون قاعدة بيانات)

def save_request_local(data: dict):
    """حفظ الطلب في الذاكرة (جلسة المستخدم فقط)"""
    st.session_state.requests.append(data)

def get_requests_local(emp_id: str):
    """إرجاع جميع طلبات موظف معين من الذاكرة"""
    return [r for r in st.session_state.requests if r["employee_id"] == emp_id]

# صفحة تسجيل الدخول

def login_page():
    st.title("🔐 تسجيل الدخول")
    st.write("أدخل رقم الموظف كما هو معرف في ملف الإعدادات.")

    emp_id = st.text_input("رقم الموظف", placeholder="مثال: 001")

    if st.button("دخول"):
        if emp_id in EMPLOYEES:
            st.session_state.logged_in = True
            st.session_state.emp_id = emp_id
            st.session_state.page = "dashboard"
            st.success(f"تم تسجيل الدخول بنجاح، أهلاً {EMPLOYEES[emp_id]['name']}")
            st.experimental_rerun()
        else:
            st.error("رقم الموظف غير صحيح، تأكد من إدخاله بشكل صحيح (مثال: 001).")

# لوحة التحكم

def dashboard_page():
    emp_id = st.session_state.emp_id
    emp = EMPLOYEES[emp_id]

    st.title("📊 لوحة التحكم الرئيسية")

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

    st.subheader("القائمة الرئيسية")
    b1, b2, b3 = st.columns(3)

    with b1:
        if st.button("➕ طلب جديد"):
            st.session_state.page = "new_request"
            st.experimental_rerun()

    with b2:
        if st.button("📝 طلباتي"):
       	    st.session_state.page = "my_requests"
            st.experimental_rerun()

    with b3:
        if st.button("✅ الموافقات (تجريبية)"):
            st.session_state.page = "approvals"
            st.experimental_rerun()

# صفحة طلب جديد

def new_request_page():
    st.title("➕ إنشاء طلب جديد")

    emp_id = st.session_state.emp_id
    emp = EMPLOYEES[emp_id]

    st.info(f"إنشاء طلب جديد للموظف: {emp['name']} - القسم: {emp['department']}")

    with st.form("new_request_form"):
        c1, c2 = st.columns(2)

        with c1:
            req_type_key = st.selectbox(
                "نوع الطلب",
                list(REQUEST_TYPES.keys()),
                format_func=lambda k: REQUEST_TYPES[k]["name"]
            )

        with c2:
            subtype = st.selectbox(
                "النوع الفرعي",
                REQUEST_TYPES[req_type_key]["subtypes"]
            )

        title = st.text_input("عنوان الطلب", placeholder="مثال: طلب إجازة سنوية")
        desc = st.text_area("وصف الطلب", placeholder="اكتب تفاصيل الطلب هنا")

        c3, c4 = st.columns(2)
        with c3:
            start = st.date_input("تاريخ البداية", value=date.today())
        with c4:
            end = st.date_input("تاريخ النهاية", value=date.today())

        submitted = st.form_submit_button("📤 إرسال الطلب")

        if submitted:
            if not title:
                st.error("عنوان الطلب مطلوب.")
                return

            if end < start:
                st.error("تاريخ النهاية لا يمكن أن يكون قبل تاريخ البداية.")
                return

            req_id = f"REQ-{datetime.now().strftime('%Y%m%d%H%M%S')}"

            data = {
                "request_id": req_id,
                "employee_id": emp_id,
                "employee_name": emp["name"],
                "request_type": req_type_key,
                "request_type_name": REQUEST_TYPES[req_type_key]["name"],
                "request_subtype": subtype,
                "title": title,
                "description": desc,
                "start_date": str(start),
                "end_date": str(end),
                "status": "pending",
                "created_at": datetime.now().isoformat(timespec="seconds"),
            }

            save_request_local(data)
            st.success(f"✅ تم إرسال الطلب بنجاح، رقم الطلب: {req_id}")

# صفحة طلباتي

def my_requests_page():
    st.title("📝 طلباتي")

    emp_id = st.session_state.emp_id
    rows = get_requests_local(emp_id)

    if not rows:
        st.info("لا توجد طلبات حتى الآن.")
        return

    df_data = [
        {
            "رقم الطلب": r["request_id"],
            "نوع الطلب": REQUEST_TYPES[r["request_type"]]["name"],
            "النوع الفرعي": r["request_subtype"],
            "العنوان": r["title"],
            "من": r["start_date"],
            "إلى": r["end_date"],
            "الحالة": r["status"],
            "تاريخ الإنشاء": r["created_at"],
        }
        for r in rows
    ]

    st.dataframe(df_data, use_container_width=True)

# صفحة الموافقات (تجريبية الآن)

def approvals_page():
    st.title("✅ صفحة الموافقات (تجريبية)")
    st.info("لاحقاً يمكن ربطها بدور المدير والإدارة العليا، الآن فقط للعرض التجريبي.")

    if not st.session_state.requests:
        st.info("لا توجد طلبات حالياً.")
        return

    df_data = [
        {
            "رقم الطلب": r["request_id"],
            "الموظف": r["employee_name"],
            "نوع الطلب": REQUEST_TYPES[r["request_type"]]["name"],
            "النوع الفرعي": r["request_subtype"],
            "العنوان": r["title"],
            "الحالة": r["status"],
        }
        for r in st.session_state.requests
    ]

    st.dataframe(df_data, use_container_width=True)

# الدالة الرئيسية

def main():
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
                st.experimental_rerun()

    # الصفحات
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
