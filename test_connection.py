"""
اختبار الاتصال بقاعدة البيانات Supabase
يتحقق من صحة الإعدادات والاتصال
"""

import sys
import os

# إضافة المجلد الرئيسي للمسار
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """اختبار استيراد المكتبات المطلوبة"""
    print("=" * 60)
    print("📦 اختبار المكتبات المطلوبة")
    print("=" * 60)
    
    required_packages = {
        'streamlit': 'Streamlit',
        'supabase': 'Supabase',
        'pandas': 'Pandas',
        'plotly': 'Plotly',
    }
    
    all_ok = True
    
    for package, name in required_packages.items():
        try:
            __import__(package)
            print(f"✅ {name:20} - مثبت")
        except ImportError:
            print(f"❌ {name:20} - غير مثبت")
            all_ok = False
    
    print()
    return all_ok


def test_config():
    """اختبار ملف الإعدادات"""
    print("=" * 60)
    print("⚙️ اختبار ملف الإعدادات")
    print("=" * 60)
    
    try:
        from config import (
            SUPABASE_URL, 
            SUPABASE_KEY, 
            USE_DATABASE,
            EMPLOYEES,
            APP_TITLE,
            APP_VERSION
        )
        
        print(f"✅ اسم التطبيق: {APP_TITLE}")
        print(f"✅ الإصدار: {APP_VERSION}")
        print(f"✅ عدد الموظفين: {len(EMPLOYEES)}")
        print(f"✅ استخدام قاعدة البيانات: {'نعم' if USE_DATABASE else 'لا'}")
        
        # التحقق من إعدادات Supabase
        if USE_DATABASE:
            if SUPABASE_URL == "https://your-project.supabase.co":
                print("⚠️ تحذير: لم تقم بتحديث SUPABASE_URL")
                return False
            if SUPABASE_KEY == "your-anon-key-here":
                print("⚠️ تحذير: لم تقم بتحديث SUPABASE_KEY")
                return False
            
            print(f"✅ رابط Supabase: {SUPABASE_URL[:30]}...")
            print(f"✅ مفتاح Supabase: {SUPABASE_KEY[:20]}...")
        
        print()
        return True
        
    except ImportError as e:
        print(f"❌ خطأ في استيراد الإعدادات: {str(e)}")
        print()
        return False


def test_supabase_connection():
    """اختبار الاتصال بـ Supabase"""
    print("=" * 60)
    print("🔌 اختبار الاتصال بـ Supabase")
    print("=" * 60)
    
    try:
        from config import SUPABASE_URL, SUPABASE_KEY, USE_DATABASE
        
        if not USE_DATABASE:
            print("ℹ️ قاعدة البيانات غير مفعّلة في config.py")
            print()
            return True
        
        from supabase import create_client
        
        print("🔄 جاري الاتصال...")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # محاولة قراءة بيانات بسيطة
        response = supabase.table('employees').select("count").execute()
        
        print("✅ الاتصال ناجح!")
        print(f"✅ قاعدة البيانات متاحة")
        print()
        return True
        
    except Exception as e:
        print(f"❌ فشل الاتصال: {str(e)}")
        print("\nتحقق من:")
        print("  1. صحة SUPABASE_URL في config.py")
        print("  2. صحة SUPABASE_KEY في config.py")
        print("  3. الاتصال بالإنترنت")
        print("  4. إنشاء الجداول في Supabase (database_setup.sql)")
        print()
        return False


def test_database_tables():
    """اختبار وجود الجداول المطلوبة"""
    print("=" * 60)
    print("🗄️ اختبار الجداول")
    print("=" * 60)
    
    try:
        from config import SUPABASE_URL, SUPABASE_KEY, USE_DATABASE
        
        if not USE_DATABASE:
            print("ℹ️ قاعدة البيانات غير مفعّلة")
            print()
            return True
        
        from supabase import create_client
        
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        tables = [
            'employees',
            'requests',
            'passports',
            'residencies',
            'activity_log',
            'notifications',
        ]
        
        all_exist = True
        
        for table in tables:
            try:
                response = supabase.table(table).select("count").execute()
                count = len(response.data) if response.data else 0
                print(f"✅ {table:20} - موجود ({count} سجل)")
            except Exception as e:
                print(f"❌ {table:20} - غير موجود")
                all_exist = False
        
        print()
        
        if not all_exist:
            print("⚠️ بعض الجداول مفقودة!")
            print("💡 قم بتشغيل: database_setup.sql في Supabase")
            print()
        
        return all_exist
        
    except Exception as e:
        print(f"❌ خطأ في فحص الجداول: {str(e)}")
        print()
        return False


def test_sample_data():
    """اختبار البيانات التجريبية"""
    print("=" * 60)
    print("📊 اختبار البيانات التجريبية")
    print("=" * 60)
    
    try:
        from config import SUPABASE_URL, SUPABASE_KEY, USE_DATABASE
        
        if not USE_DATABASE:
            print("ℹ️ قاعدة البيانات غير مفعّلة - استخدام بيانات الذاكرة")
            from config import EMPLOYEES
            print(f"✅ {len(EMPLOYEES)} موظف في config.py")
            for emp_id, emp in EMPLOYEES.items():
                print(f"   - {emp_id}: {emp['name']} ({emp['department']})")
            print()
            return True
        
        from supabase import create_client
        
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # فحص الموظفين
        response = supabase.table('employees').select("*").execute()
        if response.data:
            print(f"✅ {len(response.data)} موظف في قاعدة البيانات")
            for emp in response.data[:3]:
                print(f"   - {emp.get('id')}: {emp.get('name')} ({emp.get('department')})")
            if len(response.data) > 3:
                print(f"   ... و {len(response.data) - 3} موظف آخرين")
        else:
            print("⚠️ لا يوجد موظفين في قاعدة البيانات")
            print("💡 قم بتشغيل: python scripts/import_data.py")
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ خطأ في قراءة البيانات: {str(e)}")
        print()
        return False


def main():
    """تشغيل جميع الاختبارات"""
    
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "اختبار منصة الموارد البشرية" + " " * 18 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    results = {}
    
    # اختبار المكتبات
    results['imports'] = test_imports()
    
    # اختبار الإعدادات
    results['config'] = test_config()
    
    # اختبار الاتصال
    results['connection'] = test_supabase_connection()
    
    # اختبار الجداول
    results['tables'] = test_database_tables()
    
    # اختبار البيانات
    results['data'] = test_sample_data()
    
    # النتيجة النهائية
    print("=" * 60)
    print("📋 ملخص الاختبارات")
    print("=" * 60)
    
    test_names = {
        'imports': 'استيراد المكتبات',
        'config': 'ملف الإعدادات',
        'connection': 'الاتصال بـ Supabase',
        'tables': 'الجداول',
        'data': 'البيانات التجريبية',
    }
    
    for key, name in test_names.items():
        status = "✅ نجح" if results[key] else "❌ فشل"
        print(f"{name:30} {status}")
    
    print()
    
    all_passed = all(results.values())
    
    if all_passed:
        print("🎉 جميع الاختبارات نجحت!")
        print("✅ المنصة جاهزة للاستخدام")
        print("\nلتشغيل التطبيق:")
        print("  streamlit run app.py")
    else:
        print("⚠️ بعض الاختبارات فشلت")
        print("\nتحقق من:")
        print("  1. تثبيت جميع المكتبات: pip install -r requirements.txt")
        print("  2. إعدادات Supabase في config.py")
        print("  3. إنشاء الجداول في Supabase")
        print("  4. الاتصال بالإنترنت")
    
    print("\n" + "=" * 60 + "\n")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
