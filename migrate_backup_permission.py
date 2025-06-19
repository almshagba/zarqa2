import sqlite3
import os

# الاتصال المباشر بقاعدة البيانات
db_path = os.path.join('instance', 'employees.db')

try:
    # الاتصال بقاعدة البيانات
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # التحقق من وجود العمود أولاً
    cursor.execute("PRAGMA table_info(user)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'can_backup_database' not in columns:
        # إضافة العمود الجديد
        cursor.execute('ALTER TABLE user ADD COLUMN can_backup_database BOOLEAN DEFAULT 0')
        conn.commit()
        print("تم إضافة صلاحية النسخ الاحتياطي بنجاح")
    else:
        print("العمود موجود بالفعل")
        
except Exception as e:
    print(f"خطأ: {e}")
finally:
    if conn:
        conn.close()