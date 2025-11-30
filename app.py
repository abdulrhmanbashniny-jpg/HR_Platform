import streamlit as st
from datetime import date, datetime
from config import APP_TITLE, APP_ICON, APP_VERSION, EMPLOYEES

# إعداد صفحة Streamlit
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ثيم عربي بسيط وتحسين شكل الأزرار
st.markdown("""
<style>
    .main { direction: rtl; text-align: right; }
    header .st-emotion-cache-18ni7ap { flex-direction: row-reverse; }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# حالة الجلسة
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "emp_id" not in st.session_state:
    st.session_state.emp_id = None

if "page" not in st.session_state:
    st.session_state.page = "dashboard"  # dashboard / new_request / my_requests

if "requests" not in st.session_state:
    st.session_state.requests = []  # قائمة الطلبات في الذاكرة


# -------------------- صفحات النظام --------------------

def login_page():
    st.title("🔐 تسجيل الدخول")

    emp_id = st.text_input("رقم الموظف", placeholder="مثال: 001")

    if st.button("دخول"):
        emp_id = emp_id.strip()
        if emp_id not in EMPLOYEES:
            st.error("رقم الموظف غير موجود في النظام (جرّب 001 إلى 005).")
            return

        st.session_state.logged_in = True
        st.session_state.emp_id = emp_id
        st.session_state.page = "dashboard"
        st.rerun()


def dashboard_page():
    emp_id = st.session_state.emp_id
    emp = EMPLOYEES[emp_id]

    st.title("📊 لوحة التحكم")

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
    
    # عرض إحصائيات سريعة
    emp_requests = [r for r in st.session_state.requests if r["emp_id"] == emp_id]
    pending = len([r for r in emp_requests if r["status"] == "معلق"])
    approved = len([r for r in emp_requests if r["status"] == "موافق عليه"])
    rejected = len([r for r in emp_requests if r["status"] == "مرفوض"])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"📋 طلبات معلقة: {pending}")
    with col2:
        st.success(f"✅ طلبات موافق عليها: {approved}")
    with col3:
        st.error(f"❌ طلبات مرفوضة: {rejected}")
    
    st.divider()
    st.info("اختر من الأزرار بالأسفل لإنشاء طلب جديد أو عرض طلباتك السابقة.")

    b1, b2 = st.columns(2)
    with b1:
        if st.button("➕ طلب جديد", use_container_width=True):
            st.session_state.page = "new_request"
            st.rerun()
    with b2:
        if st.button("📝 طلباتي", use_container_width=True):
            st.session_state.page = "my_requests"
            st.rerun()


def new_request_page():
    emp_id = st.session_state.emp_id
    emp = EMPLOYEES[emp_id]

    st.title("➕ إنشاء طلب جديد")
    st.write(f"الموظف: **{emp['name']}** – القسم: **{emp['department']}**")

    # عناوين جاهزة حسب نوع الطلب
    TITLE_OPTIONS = {
        "إجازة": [
            "طلب إجازة سنوية",
            "طلب إجازة اضطرارية",
            "طلب إجازة مرضية",
        ],
        "سلفة": [
            "طلب سلفة راتب",
            "طلب سلفة طارئة",
        ],
        "استئذان": [
            "استئذان لساعات",
            "استئذان ليوم كامل",
        ],
        "رحلة عمل": [
            "رحلة عمل داخلية",
            "رحلة عمل خارجية",
        ],
        "طلب شراء": [
            "طلب شراء معدات تقنية",
            "طلب شراء أدوات مكتبية",
            "طلب شراء خدمات",
        ],
    }

    with st.form("new_request_form"):
        request_type = st.selectbox(
            "نوع الطلب",
            list(TITLE_OPTIONS.keys()),
        )

        title = st.selectbox(
            "عنوان الطلب",
            TITLE_OPTIONS[request_type],
        )

        details = st.text_area("تفاصيل الطلب", placeholder="اكتب تفاصيل الطلب هنا (اختياري)")

        # حقول حسب نوع الطلب
        if request_type in ["إجازة", "رحلة عمل"]:
            c1, c2 = st.columns(2)
            with c1:
                start_date = st.date_input("تاريخ البداية", value=date.today())
            with c2:
                end_date = st.date_input("تاريخ النهاية", value=date.today())
        elif request_type == "استئذان":
            day = st.date_input("تاريخ الاستئذان", value=date.today())
            hours = st.number_input("عدد الساعات", min_value=1, max_value=12, value=2)
            start_date = end_date = day
            details = details or f"استئذان لمدة {hours} ساعة."
        else:  # سلفة / طلب شراء
            start_date = end_date = date.today()

        submitted = st.form_submit_button("📤 إرسال الطلب", use_container_width=True)

    if submitted:
        if request_type in ["إجازة", "رحلة عمل"] and end_date < start_date:
            st.error("تاريخ النهاية لا يمكن أن يكون قبل تاريخ البداية.")
            return

        req_id = f"REQ-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        st.session_state.requests.append(
            {
                "id": req_id,
                "emp_id": emp_id,
                "emp_name": emp["name"],
                "type": request_type,
                "title": title,
                "details": details,
                "start": str(start_date),
                "end": str(end_date),
                "status": "معلق",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
        st.success(f"✅ تم حفظ الطلب برقم: {req_id}")
        st.info("يمكنك مشاهدة الطلب من صفحة \"طلباتي\".")

    st.divider()
    if st.button("⬅ العودة للوحة التحكم"):
        st.session_state.page = "dashboard"
        st.rerun()


def my_requests_page():
    emp_id = st.session_state.emp_id
    emp_requests = [r for r in st.session_state.requests if r["emp_id"] == emp_id]

    st.title("📝 طلباتي")

    if not emp_requests:
        st.info("لا توجد طلبات مسجلة حتى الآن.")
        if st.button("➕ إنشاء أول طلب"):
            st.session_state.page = "new_request"
            st.rerun()
    else:
        # فلترة حسب الحالة
        status_filter = st.selectbox(
            "فلترة حسب الحالة",
            ["الكل", "معلق", "موافق عليه", "مرفوض"]
        )
        
        filtered_requests = emp_requests
        if status_filter != "الكل":
            filtered_requests = [r for r in emp_requests if r["status"] == status_filter]
        
        st.write(f"**عدد الطلبات:** {len(filtered_requests)}")
        
        for r in filtered_requests[::-1]:
            status_color = {
                "معلق": "🟡",
                "موافق عليه": "🟢",
                "مرفوض": "🔴"
            }.get(r['status'], "⚪")
            
            with st.expander(f"{status_color} {r['id']} - {r['title']} ({r['status']})"):
                st.write(f"**النوع:** {r['type']}")
                st.write(f"**من:** {r['start']} – **إلى:** {r['end']}")
                st.write(f"**التفاصيل:** {r['details'] or 'لا يوجد'}")
                st.write(f"**تاريخ الإنشاء:** {r['created_at']}")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅ العودة للوحة التحكم", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()
    with col2:
        if st.button("➕ طلب جديد", use_container_width=True):
            st.session_state.page = "new_request"
            st.rerun()


# -------------------- الدالة الرئيسية --------------------

def main():
    with st.sidebar:
        st.title(APP_TITLE)
        st.write(f"الإصدار: {APP_VERSION}")
        st.divider()
        if st.session_state.logged_in:
            emp = EMPLOYEES[st.session_state.emp_id]
            st.write(f"👤 {emp['name']}")
            st.write(f"🏢 {emp['department']}")
            st.write(f"💼 {emp['role']}")
            st.divider()
            if st.button("🚪 تسجيل خروج", use_container_width=True):
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


if __name__ == "__main__":
    main()
