import streamlit as st
import pandas as pd
from datetime import datetime

# محاكاة لقاعدة البيانات (يجب استبدالها بملف CSV أو SQL)
if 'requests_db' not in st.session_state:
    st.session_state.requests_db = []

# تعريف الأدوار والمراحل
STAGES = {
    1: "Employee",        # تقديم الطلب
    2: "Supervisor",      # مشرف القسم
    3: "Dept_Manager",    # مدير القسم
    4: "HR_Manager",      # مدير الموارد البشرية
    5: "Finance_Manager", # مدير مالي
    6: "Completed"        # مكتمل
}

# دالة تقديم طلب جديد (للموظف)
def submit_request(emp_name, req_type, details):
    new_req = {
        "id": len(st.session_state.requests_db) + 1,
        "employee": emp_name,
        "type": req_type,
        "details": details,
        "current_stage": 2,  # ينتقل مباشرة للمشرف
        "status": "Pending", # معلق
        "history": [f"{datetime.now()}: تم تقديم الطلب بواسطة {emp_name}"]
    }
    st.session_state.requests_db.append(new_req)
    st.success("تم إرسال الطلب للمشرف بنجاح!")

# دالة معالجة الطلب (للمدراء والمشرفين)
def process_request(request_id, action, reviewer_role, reason=""):
    # البحث عن الطلب
    for req in st.session_state.requests_db:
        if req['id'] == request_id:
            
            # تسجيل العملية في السجل
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            if action == "approve":
                # منطق الانتقال للمرحلة التالية
                current_stage = req['current_stage']
                
                # التحقق من أن الموافق هو الشخص الصحيح في المرحلة الصحيحة
                # (يمكن تبسيط هذا الشرط، لكن للتوضيح)
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
                    req['status'] = "Approved" # موافقة نهائية
                    req['history'].append(f"{timestamp}: وافق المدير المالي - اكتمل الطلب")
                
                st.success(f"تمت الموافقة! انتقل الطلب للمرحلة التالية.")

            elif action == "reject":
                req['status'] = "Rejected"
                req['current_stage'] = 0 # إيقاف الطلب
                req['history'].append(f"{timestamp}: تم الرفض بواسطة {reviewer_role}. السبب: {reason}")
                st.error("تم رفض الطلب.")
            
            return

# --- واجهة المستخدم ---

# تسجيل الدخول الوهمي (للتجربة)
user_role = st.sidebar.selectbox("تسجيل الدخول بصفتك:", 
                                 ["الموظف", "مشرف القسم", "مدير القسم", "مدير الموارد البشرية", "مدير مالي", "مدير النظام"])

st.title(f"لوحة تحكم: {user_role}")

# 1. واجهة الموظف
if user_role == "الموظف":
    st.subheader("طلب جديد")
    r_type = st.selectbox("نوع الطلب", ["إجازة", "سلفة"])
    details = st.text_area("التفاصيل")
    if st.button("إرسال"):
        submit_request("أحمد محمد", r_type, details)

# 2. واجهة المدراء والمشرفين (نظام الفلترة الذكي)
else:
    st.subheader("الطلبات الواردة")
    
    # تحديد المرحلة التي يجب أن يراها هذا المستخدم
    target_stage = 0
    if user_role == "مشرف القسم": target_stage = 2
    elif user_role == "مدير القسم": target_stage = 3
    elif user_role == "مدير الموارد البشرية": target_stage = 4
    elif user_role == "مدير مالي": target_stage = 5
    
    # عرض الطلبات الخاصة بهذه المرحلة فقط + الطلبات المعلقة
    pending_requests = [r for r in st.session_state.requests_db 
                       if r['current_stage'] == target_stage and r['status'] == 'Pending']
    
    if not pending_requests:
        st.info("لا توجد طلبات بانتظار موافقتك.")
    
    for req in pending_requests:
        with st.expander(f"طلب #{req['id']} - {req['type']} من {req['employee']}"):
            st.write(f"**التفاصيل:** {req['details']}")
            st.write("**سجل الموافقات:**")
            for log in req['history']:
                st.text(log)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("موافقة ✅", key=f"app_{req['id']}"):
                    process_request(req['id'], "approve", user_role)
                    st.rerun()
            with col2:
                reason_reject = st.text_input("سبب الرفض", key=f"reason_{req['id']}")
                if st.button("رفض ❌", key=f"rej_{req['id']}"):
                    if reason_reject:
                        process_request(req['id'], "reject", user_role, reason_reject)
                        st.rerun()
                    else:
                        st.warning("يجب كتابة سبب الرفض.")

# عرض قاعدة البيانات للمراقبة (فقط لمدير النظام)
if user_role == "مدير النظام":
    st.write("---")
    st.write("📊 كل الطلبات في النظام")
    if st.session_state.requests_db:
        st.table(pd.DataFrame(st.session_state.requests_db))
