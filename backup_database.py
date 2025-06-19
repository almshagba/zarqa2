import shutil
import os
from datetime import datetime

def backup_database():
    # مسار قاعدة البيانات الأصلية
    source_db = 'instance/employees.db'
    
    # إنشاء مجلد النسخ الاحتياطية إذا لم يكن موجوداً
    backup_dir = 'backups'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # إنشاء اسم الملف مع التاريخ والوقت
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    backup_filename = f'employees_backup_{timestamp}.db'
    backup_path = os.path.join(backup_dir, backup_filename)
    
    try:
        # نسخ قاعدة البيانات
        shutil.copy2(source_db, backup_path)
        print(f'تم إنشاء النسخة الاحتياطية بنجاح: {backup_path}')
        
        # حذف النسخ القديمة (الاحتفاظ بآخر 10 نسخ فقط)
        cleanup_old_backups(backup_dir)
        
    except Exception as e:
        print(f'خطأ في إنشاء النسخة الاحتياطية: {e}')

def cleanup_old_backups(backup_dir, keep_count=10):
    """حذف النسخ الاحتياطية القديمة والاحتفاظ بعدد محدد من النسخ الحديثة"""
    try:
        # الحصول على قائمة ملفات النسخ الاحتياطية
        backup_files = [f for f in os.listdir(backup_dir) if f.startswith('employees_backup_') and f.endswith('.db')]
        
        # ترتيب الملفات حسب تاريخ الإنشاء
        backup_files.sort(key=lambda x: os.path.getctime(os.path.join(backup_dir, x)), reverse=True)
        
        # حذف الملفات الزائدة
        for file_to_delete in backup_files[keep_count:]:
            file_path = os.path.join(backup_dir, file_to_delete)
            os.remove(file_path)
            print(f'تم حذف النسخة القديمة: {file_to_delete}')
            
    except Exception as e:
        print(f'خطأ في تنظيف النسخ القديمة: {e}')

if __name__ == '__main__':
    backup_database()