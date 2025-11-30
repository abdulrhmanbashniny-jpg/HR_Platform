"""
سكريبت النسخ الاحتياطية التلقائية
يقوم بحفظ نسخ من قاعدة البيانات بشكل دوري
"""

import os
import sys
from datetime import datetime
import json
from pathlib import Path

# إضافة المجلد الرئيسي للمسار
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from supabase import create_client
    from config import SUPABASE_URL, SUPABASE_KEY, USE_DATABASE
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("⚠️ مكتبة Supabase غير مثبتة. استخدم: pip install supabase")

# إنشاء مجلد النسخ الاحتياطية
BACKUP_DIR = Path("backups")
BACKUP_DIR.mkdir(exist_ok=True)


def backup_table(supabase, table_name, backup_file):
    """نسخ احتياطي لجدول واحد"""
    try:
        print(f"  📦 نسخ جدول: {table_name}...")
        
        # جلب جميع البيانات
        response = supabase.table(table_name).select("*").execute()
        
        if response.data:
            # حفظ البيانات
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(response.data, f, ensure_ascii=False, indent=2)
            
            print(f"  ✅ تم حفظ {len(response.data)} سجل من {table_name}")
            return len(response.data)
        else:
            print(f"  ℹ️ جدول {table_name} فارغ")
            return 0
            
    except Exception as e:
        print(f"  ❌ خطأ في نسخ {table_name}: {str(e)}")
        return 0


def create_backup():
    """إنشاء نسخة احتياطية كاملة"""
    
    if not SUPABASE_AVAILABLE:
        print("❌ لا يمكن إنشاء نسخة احتياطية - Supabase غير متوفر")
        return False
    
    if not USE_DATABASE:
        print("❌ قاعدة البيانات غير مفعّلة في config.py")
        return False
    
    print("=" * 60)
    print("🚀 بدء النسخ الاحتياطي")
    print("=" * 60)
    
    # إنشاء اتصال
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ تم الاتصال بقاعدة البيانات")
    except Exception as e:
        print(f"❌ فشل الاتصال: {str(e)}")
        return False
    
    # تحديد التاريخ والوقت
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_folder = BACKUP_DIR / f"backup_{timestamp}"
    backup_folder.mkdir(exist_ok=True)
    
    print(f"📁 مجلد النسخة: {backup_folder}")
    
    # قائمة الجداول
    tables = [
        "employees",
        "requests",
        "passports",
        "residencies",
        "activity_log",
        "notifications",
    ]
    
    total_records = 0
    
    # نسخ كل جدول
    for table in tables:
        backup_file = backup_folder / f"{table}.json"
        records = backup_table(supabase, table, backup_file)
        total_records += records
    
    # إنشاء ملف معلومات النسخة
    info = {
        "timestamp": timestamp,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_records": total_records,
        "tables": tables,
    }
    
    info_file = backup_folder / "backup_info.json"
    with open(info_file, 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print(f"✅ اكتمل النسخ الاحتياطي!")
    print(f"📊 إجمالي السجلات: {total_records}")
    print(f"📁 الموقع: {backup_folder}")
    print("=" * 60)
    
    return True


def restore_backup(backup_folder):
    """استعادة نسخة احتياطية"""
    
    if not SUPABASE_AVAILABLE:
        print("❌ لا يمكن استعادة النسخة - Supabase غير متوفر")
        return False
    
    backup_path = Path(backup_folder)
    
    if not backup_path.exists():
        print(f"❌ المجلد غير موجود: {backup_folder}")
        return False
    
    print("=" * 60)
    print("🔄 بدء استعادة النسخة الاحتياطية")
    print("=" * 60)
    
    # إنشاء اتصال
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ تم الاتصال بقاعدة البيانات")
    except Exception as e:
        print(f"❌ فشل الاتصال: {str(e)}")
        return False
    
    # قراءة معلومات النسخة
    info_file = backup_path / "backup_info.json"
    if info_file.exists():
        with open(info_file, 'r', encoding='utf-8') as f:
            info = json.load(f)
        print(f"📅 تاريخ النسخة: {info['date']}")
        print(f"📊 عدد السجلات: {info['total_records']}")
    
    # استعادة كل جدول
    total_restored = 0
    
    for json_file in backup_path.glob("*.json"):
        if json_file.name == "backup_info.json":
            continue
        
        table_name = json_file.stem
        print(f"\n  📥 استعادة جدول: {table_name}...")
        
        try:
            # قراءة البيانات
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not data:
                print(f"  ℹ️ {table_name} فارغ")
                continue
            
            # إدراج البيانات
            for record in data:
                try:
                    supabase.table(table_name).upsert(record).execute()
                except Exception as e:
                    print(f"  ⚠️ خطأ في سجل: {str(e)}")
            
            print(f"  ✅ تمت استعادة {len(data)} سجل")
            total_restored += len(data)
            
        except Exception as e:
            print(f"  ❌ خطأ في استعادة {table_name}: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"✅ اكتملت الاستعادة!")
    print(f"📊 إجمالي السجلات المستعادة: {total_restored}")
    print("=" * 60)
    
    return True


def list_backups():
    """عرض قائمة النسخ الاحتياطية المتوفرة"""
    
    print("=" * 60)
    print("📋 النسخ الاحتياطية المتوفرة")
    print("=" * 60)
    
    backups = sorted(BACKUP_DIR.glob("backup_*"), reverse=True)
    
    if not backups:
        print("ℹ️ لا توجد نسخ احتياطية")
        return []
    
    for i, backup in enumerate(backups, 1):
        info_file = backup / "backup_info.json"
        if info_file.exists():
            with open(info_file, 'r', encoding='utf-8') as f:
                info = json.load(f)
            print(f"{i}. {backup.name}")
            print(f"   📅 التاريخ: {info['date']}")
            print(f"   📊 السجلات: {info['total_records']}")
            print()
        else:
            print(f"{i}. {backup.name}")
            print(f"   ⚠️ ملف المعلومات مفقود")
            print()
    
    return backups


def clean_old_backups(days=30):
    """حذف النسخ الاحتياطية القديمة"""
    
    print("=" * 60)
    print("🧹 تنظيف النسخ الاحتياطية القديمة")
    print("=" * 60)
    
    from datetime import timedelta
    
    cutoff_date = datetime.now() - timedelta(days=days)
    deleted = 0
    
    for backup in BACKUP_DIR.glob("backup_*"):
        # استخراج التاريخ من اسم المجلد
        try:
            date_str = backup.name.replace("backup_", "").split("_")[0]
            backup_date = datetime.strptime(date_str, "%Y%m%d")
            
            if backup_date < cutoff_date:
                import shutil
                shutil.rmtree(backup)
                print(f"  🗑️ تم حذف: {backup.name}")
                deleted += 1
                
        except Exception as e:
            print(f"  ⚠️ خطأ في معالجة {backup.name}: {str(e)}")
    
    if deleted == 0:
        print("  ℹ️ لا توجد نسخ قديمة للحذف")
    else:
        print(f"\n✅ تم حذف {deleted} نسخة قديمة")
    
    print("=" * 60)


def main():
    """القائمة الرئيسية"""
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "create":
            create_backup()
            
        elif command == "restore":
            if len(sys.argv) > 2:
                restore_backup(sys.argv[2])
            else:
                backups = list_backups()
                if backups:
                    print("استخدم: python backup.py restore backups/backup_YYYYMMDD_HHMMSS")
                    
        elif command == "list":
            list_backups()
            
        elif command == "clean":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            clean_old_backups(days)
            
        else:
            print(f"❌ أمر غير معروف: {command}")
            print_usage()
    else:
        print_usage()


def print_usage():
    """عرض تعليمات الاستخدام"""
    print("""
استخدام سكريبت النسخ الاحتياطي:

  python backup.py create              # إنشاء نسخة احتياطية جديدة
  python backup.py list                # عرض النسخ المتوفرة
  python backup.py restore [مجلد]     # استعادة نسخة محددة
  python backup.py clean [أيام]       # حذف النسخ القديمة (الافتراضي: 30 يوم)

أمثلة:
  python backup.py create
  python backup.py list
  python backup.py restore backups/backup_20251130_120530
  python backup.py clean 60
    """)


if __name__ == "__main__":
    main()
