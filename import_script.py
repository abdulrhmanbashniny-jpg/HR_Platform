"""
سكريبت استيراد البيانات من ملفات Excel إلى Supabase
"""

import pandas as pd
from supabase import create_client
import sys
import os
from datetime import datetime

# إضافة المجلد الرئيسي للمسار
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import SUPABASE_URL, SUPABASE_KEY

# الاتصال بـ Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def import_employees(file_path='data/employees.xlsx'):
    """استيراد بيانات الموظفين"""
    print("📥 استيراد بيانات الموظفين...")
    
    try:
        df = pd.read_excel(file_path)
        
        # تنظيف البيانات
        df = df.fillna('')
        
        # تحويل إلى قائمة من القواميس
        employees = df.to_dict('records')
        
        # إدراج البيانات
        for emp in employees:
            try:
                result = supabase.table('employees').upsert(emp).execute()
                print(f"  ✅ تم استيراد: {emp.get('name', 'غير معروف')}")
            except Exception as e:
                print(f"  ❌ خطأ في: {emp.get('name', 'غير معروف')} - {str(e)}")
        
        print(f"✅ تم استيراد {len(employees)} موظف بنجاح!")
        
    except FileNotFoundError:
        print(f"❌ الملف غير موجود: {file_path}")
    except Exception as e:
        print(f"❌ خطأ في استيراد الموظفين: {str(e)}")


def import_requests(file_path='data/requests.xlsx'):
    """استيراد بيانات الطلبات"""
    print("\n📥 استيراد بيانات الطلبات...")
    
    try:
        df = pd.read_excel(file_path)
        
        # تنظيف البيانات
        df = df.fillna('')
        
        # تحويل التواريخ
        date_columns = ['start_date', 'end_date', 'created_at']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d')
        
        # تحويل إلى قائمة من القواميس
        requests = df.to_dict('records')
        
        # إدراج البيانات
        for req in requests:
            try:
                result = supabase.table('requests').upsert(req).execute()
                print(f"  ✅ تم استيراد: {req.get('id', 'غير معروف')}")
            except Exception as e:
                print(f"  ❌ خطأ في: {req.get('id', 'غير معروف')} - {str(e)}")
        
        print(f"✅ تم استيراد {len(requests)} طلب بنجاح!")
        
    except FileNotFoundError:
        print(f"❌ الملف غير موجود: {file_path}")
    except Exception as e:
        print(f"❌ خطأ في استيراد الطلبات: {str(e)}")


def import_passports(file_path='data/muqeem.xlsx', sheet_name='جوازات'):
    """استيراد بيانات الجوازات"""
    print("\n📥 استيراد بيانات الجوازات...")
    
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        # تنظيف البيانات
        df = df.fillna('')
        
        # تحويل التواريخ
        date_columns = ['issue_date', 'expiry_date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d')
        
        # تحويل إلى قائمة من القواميس
        passports = df.to_dict('records')
        
        # إدراج البيانات
        for passport in passports:
            try:
                result = supabase.table('passports').upsert(passport).execute()
                print(f"  ✅ تم استيراد جواز: {passport.get('passport_number', 'غير معروف')}")
            except Exception as e:
                print(f"  ❌ خطأ في: {passport.get('passport_number', 'غير معروف')} - {str(e)}")
        
        print(f"✅ تم استيراد {len(passports)} جواز سفر بنجاح!")
        
    except FileNotFoundError:
        print(f"❌ الملف غير موجود: {file_path}")
    except Exception as e:
        print(f"❌ خطأ في استيراد الجوازات: {str(e)}")


def import_residencies(file_path='data/muqeem.xlsx', sheet_name='إقامات'):
    """استيراد بيانات الإقامات"""
    print("\n📥 استيراد بيانات الإقامات...")
    
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        # تنظيف البيانات
        df = df.fillna('')
        
        # تحويل التواريخ
        date_columns = ['issue_date', 'expiry_date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d')
        
        # تحويل إلى قائمة من القواميس
        residencies = df.to_dict('records')
        
        # إدراج البيانات
        for residency in residencies:
            try:
                result = supabase.table('residencies').upsert(residency).execute()
                print(f"  ✅ تم استيراد إقامة: {residency.get('residency_number', 'غير معروف')}")
            except Exception as e:
                print(f"  ❌ خطأ في: {residency.get('residency_number', 'غير معروف')} - {str(e)}")
        
        print(f"✅ تم استيراد {len(residencies)} إقامة بنجاح!")
        
    except FileNotFoundError:
        print(f"❌ الملف غير موجود: {file_path}")
    except Exception as e:
        print(f"❌ خطأ في استيراد الإقامات: {str(e)}")


def main():
    """الدالة الرئيسية"""
    print("=" * 60)
    print("🚀 بدء استيراد البيانات إلى Supabase")
    print("=" * 60)
    
    # التحقق من الاتصال
    try:
        result = supabase.table('employees').select("count").execute()
        print("✅ الاتصال بـ Supabase ناجح!")
    except Exception as e:
        print(f"❌ فشل الاتصال بـ Supabase: {str(e)}")
        return
    
    # استيراد جميع البيانات
    import_employees()
    import_requests()
    import_passports()
    import_residencies()
    
    print("\n" + "=" * 60)
    print("✅ اكتمل استيراد جميع البيانات!")
    print("=" * 60)


if __name__ == "__main__":
    main()
