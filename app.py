import streamlit as st
import pandas as pd
from datetime import datetime
import time

# --- إعدادات الصفحة ---
st.set_page_config(
    page_title="منصة إدارة الموارد البشرية",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- قاعدة بيانات وهمية (للتجربة) ---
# في الواقع يجب أن تكون في ملف CSV أو SQL
# كلمات المرور هنا بسيطة (123) لكل الموظفين للتجربة
USERS_DB = {
    "1001": {"name": "أحمد محمد", "role": "الموظف", "password": "123", "dept": "IT"},
    "1002": {"name": "سارة علي", "role": "مشرف القسم", "password": "123", "dept": "IT"},
    "1003": {"name": "خالد عمر", "role": "مدير القسم", "password": "123", "dept": "IT"},
    "1004": {"name": "منى سعيد", "role": "مدير الموارد البشرية", "password": "123", "dept": "HR"},
    "1005": {"name": "فهد ناصر", "role": "مدير مالي", "password": "123", "dept": "Finance"},
    "9999": {"name": "Admin", "role": "مدير النظام", "password": "admin", "dept": "Admin"}
}

# --- تهيئة الذاكرة (Session State) ---
if 'requests_db' not in st.session_state:
    st.session_state.requests_db = []

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'user_info' not in st.session_state:
    st.session_state.user_info = None

# --- دوال المساعدة ---

def login(emp_id, password):
    """التحقق من بيانات الدخول"""
    if emp_id in USERS_DB:
        user = USERS_DB[emp_id]
        if user['password'] == password:
            st.session_state.logged_in = True
            st.session_state.user_info = user
            st.session_state.user_id = emp_id
            return True
    return False

def logout():
    """تسجيل الخروج"""
    st.session_state.logged_in = False
    st.session_state.user_info = None
    st.rerun()

def submit_request(emp_name, emp_id, req_type, req_title, start_date, end_date, loan_amount, reason):
    """تقديم طلب جديد"""
    new_req = {
        "id": len(st.session_state.requests_db) + 1,
        "emp_id": emp_id,
        "employee": emp_name,
        "type": req_type,
        "title": req_title,
        "start_date": str(start_date) if start_date else None,
        "end_date": str(end_date) if end_date else None,
        "loan_amount": loan_amount,
        "reason": reason,
        "current_stage": 2,  # يبدأ عند المشرف (المرحلة 2)
        "status": "Pending",
        "history": [f"{datetime.now().strftime('%Y-%m-%d %H:%M')}: تم تقديم الطلب"]
    }
    st.session_state.requests_db.append(new_req)

def process_request(request_id, action, reviewer_role, reason=""):
    """معالجة الطلب (موافقة/رفض)"""
    for req in st.session_state.requests_db:
        if req['id'] == request_id:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            if action == "approve":
                current_stage = req['current_stage']
                
                # سلسلة الموافقات
                if reviewer_role == "مشرف القسم" and current_stage == 2:
                    req['current_stage'] = 3
                    req['history'].append(f"{timestamp}: وافق مشرف القسم")
                elif reviewer_role == "مدير القسم" and current_stage == 3:
                    req['current_stage'] = 4
                    req['history'].append(f"{timestamp}: وافق مدير القسم")
                elif reviewer_role == "مدير الموارد البشرية" and current_stage == 4:
                    req['current_stage'] = 5
                    req['history'].append(f"{timestamp}: وافق مدير الموارد البشرية")
                elif reviewer_role == "مدير مالي" and current_stage == 5:
                    req['current_stage'] = 6
                    req['status'] = "Approved"
                    req['history'].append(f"{timestamp}: وافق المدير المالي - اكتمل الطلب")
                
                st.success("✅ تم تسجيل الموافقة")
                time.sleep(1)
                st.rerun()

            elif action == "reject":
                req['status'] = "Rejected"
                req['current_stage'] = 0
                req['history'].append(f"{timestamp}: تم الرفض بواسطة {reviewer_role}. السبب: {reason}")
                st.error("❌ تم رفض الطلب")
                time.sleep(1)
                st.rerun()
            return

# --- الواجهة الرئيسية ---

if not st.session_state.logged_in:
    # صفحة تسجيل الدخول
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔒 تسجيل الدخول")
        st.markdown("### منصة إدارة الموارد البشرية")
        
        emp_id_input = st.text_input("رقم الموظف", placeholder="مثال: 1001")
        password_input = st.text_input("كلمة المرور", type="password")
        
        if st.button("دخول", use_container_width=True):
            if login(emp_id_input, password_input):
                st.success("تم الدخول بنجاح!")
                st.rerun()
            else:
                st.error("خطأ في رقم الموظف أو كلمة المرور")
                
        with st.expander("ℹ️ بيانات تجريبية للدخول"):
            st.code("""
            الموظف: 1001 / 123
            مشرف القسم: 1002 / 123
            مدير القسم: 1003 / 123
            مدير HR: 1004 / 123
            مدير مالي: 1005 / 123
            """)

else:
    # واجهة النظام بعد الدخول
    user = st.session_state.user_info
    
    # الشريط الجانبي
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
        st.title(f"مرحباً، {user['name']}")
        st.info(f"المنصب: {user['role']}")
        
        if st.button("تسجيل خروج"):
            logout()

    # --- المحتوى الرئيسي حسب الدور ---
    
    # 1. واجهة الموظف (تقديم الطلبات)
    if user['role'] == "الموظف":
        st.header("📝 تقديم طلب جديد")
        
        # نوع الطلب وتحديث القوائم
        req_type = st.selectbox("نوع الطلب", ["طلب إجازة", "سلفة", "تعريف راتب", "أخرى"])
        
        req_titles = []
        if req_type == "طلب إجازة":
            req_titles = ["إجازة سنوية", "إجازة اضطرارية", "إجازة مرضية"]
        elif req_type == "سلفة":
            req_titles = ["سلفة زواج", "سلفة سيارة", "سلفة شخصية"]
        elif req_type == "تعريف راتب":
            req_titles = ["تعريف للبنك", "تعريف للسفارة"]
        else:
            req_titles = ["طلب عام"]
            
        req_title = st.selectbox("عنوان الطلب", req_titles)
        
        # الحقول الديناميكية
        start_d, end_d, amount = None, None, 0
        
        if req_type == "طلب إجازة":
            c1, c2 = st.columns(2)
            start_d = c1.date_input("تاريخ البداية")
            end_d = c2.date_input("تاريخ النهاية")
        elif req_type == "سلفة":
            amount = st.number_input("مبلغ السلفة", step=500, min_value=0)
            
        reason_text = st.text_area("ملاحظات / السبب")
        
        if st.button("إرسال الطلب", type="primary"):
            submit_request(user['name'], st.session_state.user_id, req_type, req_title, start_d, end_d, amount, reason_text)
            st.success("تم إرسال الطلب بنجاح للمشرف!")
            
        # عرض طلبات الموظف السابقة
        st.divider()
        st.subheader("📂 طلباتي السابقة")
        my_requests = [r for r in st.session_state.requests_db if r['emp_id'] == st.session_state.user_id]
        if my_requests:
            st.table(pd.DataFrame(my_requests)[['id', 'type', 'title', 'status', 'current_stage']])
        else:
            st.info("لا توجد طلبات سابقة.")

    # 2. واجهة المدراء (الموافقات)
    else:
        st.header("🗂 لوحة الموافقات")
        
        # تحديد المرحلة المستهدفة لهذا المدير
        target_stage = 0
        if user['role'] == "مشرف القسم": target_stage = 2
        elif user['role'] == "مدير القسم": target_stage = 3
        elif user['role'] == "مدير الموارد البشرية": target_stage = 4
        elif user['role'] == "مدير مالي": target_stage = 5
        
        # جلب الطلبات المعلقة لهذه المرحلة
        pending = [r for r in st.session_state.requests_db if r['current_stage'] == target_stage and r['status'] == "Pending"]
        
        if not pending:
            st.success("🎉 لا توجد طلبات معلقة بانتظارك.")
        
        for req in pending:
            with st.expander(f"طلب #{req['id']} | {req['type']} - {req['employee']}", expanded=True):
                c1, c2 = st.columns([2, 1])
                with c1:
                    st.markdown(f"**عنوان الطلب:** {req['title']}")
                    st.markdown(f"**الملاحظات:** {req['reason']}")
                    if req['type'] == "سلفة":
                        st.markdown(f"💵 **المبلغ:** {req['loan_amount']}")
                    if req['type'] == "طلب إجازة":
                        st.markdown(f"📅 **من:** {req['start_date']} **إلى:** {req['end_date']}")
                    
                    st.caption("سجل العمليات:")
                    for h in req['history']:
                        st.text(h)
                        
                with c2:
                    st.write("---")
                    if st.button("✅ موافقة", key=f"ok_{req['id']}", use_container_width=True):
                        process_request(req['id'], "approve", user['role'])
                    
                    reject_reason = st.text_input("سبب الرفض", key=f"reason_{req['id']}")
                    if st.button("❌ رفض", key=f"no_{req['id']}", use_container_width=True):
                        if reject_reason:
                            process_request(req['id'], "reject", user['role'], reject_reason)
                        else:
                            st.warning("اكتب سبب الرفض أولاً")

    # 3. (إضافي) عرض جدول البيانات لمدير النظام فقط
    if user['role'] == "مدير النظام":
        st.divider()
        st.subheader("قاعدة البيانات الكاملة")
        if st.session_state.requests_db:
            st.dataframe(st.session_state.requests_db)
