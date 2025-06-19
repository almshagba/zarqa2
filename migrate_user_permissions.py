import sqlite3
import os

def add_user_permissions():
    # مسار قاعدة البيانات
    db_path = os.path.join('instance', 'employees.db')
    
    if not os.path.exists(db_path):
        print(f"خطأ: لم يتم العثور على قاعدة البيانات في {db_path}")
        return
    
    try:
        # الاتصال بقاعدة البيانات
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # التحقق من وجود الأعمدة أولاً
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # قائمة الأعمدة الجديدة
        new_columns = [
            'can_manage_employees',
            'can_manage_schools', 
            'can_manage_leaves',
            'can_manage_departures',
            'can_manage_transfers',
            'can_view_reports',
            'can_export_data',
            'can_manage_users',
            'can_manage_forms',
            'can_process_monthly_departures'
        ]
        
        # إضافة الأعمدة التي لا توجد
        for column in new_columns:
            if column not in columns:
                try:
                    cursor.execute(f'ALTER TABLE user ADD COLUMN {column} BOOLEAN DEFAULT 0')
                    print(f"تم إضافة العمود: {column}")
                except sqlite3.OperationalError as e:
                    print(f"خطأ في إضافة العمود {column}: {e}")
            else:
                print(f"العمود {column} موجود بالفعل")
        
        # حفظ التغييرات
        conn.commit()
        print("\nتم إضافة جميع حقول الصلاحيات بنجاح!")
        
        # إعطاء جميع الصلاحيات للمستخدمين الإداريين الحاليين
        cursor.execute("SELECT id, username FROM user WHERE is_admin = 1")
        admin_users = cursor.fetchall()
        
        if admin_users:
            print("\nإعطاء جميع الصلاحيات للمستخدمين الإداريين:")
            for user_id, username in admin_users:
                update_query = f"""
                UPDATE user SET 
                    can_manage_employees = 1,
                    can_manage_schools = 1,
                    can_manage_leaves = 1,
                    can_manage_departures = 1,
                    can_manage_transfers = 1,
                    can_view_reports = 1,
                    can_export_data = 1,
                    can_manage_users = 1,
                    can_manage_forms = 1,
                    can_process_monthly_departures = 1
                WHERE id = ?
                """
                cursor.execute(update_query, (user_id,))
                print(f"- تم إعطاء جميع الصلاحيات للمستخدم: {username}")
            
            conn.commit()
        
    except sqlite3.Error as e:
        print(f"خطأ في قاعدة البيانات: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    add_user_permissions()