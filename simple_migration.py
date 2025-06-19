# -*- coding: utf-8 -*-
"""
سكريبت بسيط لترحيل قاعدة البيانات إلى النظام الجديد للصلاحيات
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """ترحيل قاعدة البيانات"""
    db_path = 'instance/employees.db'
    
    if not os.path.exists(db_path):
        print(f"❌ لم يتم العثور على قاعدة البيانات: {db_path}")
        return False
    
    try:
        # الاتصال بقاعدة البيانات
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 بدء ترحيل قاعدة البيانات...")
        
        # قائمة الأعمدة الجديدة المطلوبة
        new_columns = [
            'can_view_employees_list',
            'can_view_employee_details', 
            'can_edit_employees_data',
            'can_add_new_employee',
            'can_delete_employee',
            'can_view_schools_list',
            'can_view_school_details',
            'can_edit_schools_data', 
            'can_add_new_school',
            'can_delete_school',
            'can_view_leaves_list',
            'can_view_leave_details',
            'can_edit_leaves_data',
            'can_add_new_leave', 
            'can_delete_leave',
            'can_manage_leave_balances',
            'can_view_departures_list',
            'can_view_departure_details',
            'can_edit_departures_data',
            'can_add_new_departure',
            'can_delete_departure',
            'can_view_transfers_list',
            'can_view_transfer_details', 
            'can_edit_transfers_data',
            'can_add_new_transfer',
            'can_delete_transfer',
            'can_view_employee_reports',
            'can_view_school_reports',
            'can_view_comprehensive_reports',
            'can_export_employee_data',
            'can_export_school_data',
            'can_export_report_data',
            'can_view_users_list',
            'can_add_new_user',
            'can_manage_user_permissions',
            'can_view_forms_list',
            'can_edit_forms_data',
            'can_add_new_form',
            'can_delete_form',
            'can_view_system_logs',
            'can_manage_system_settings',
            'can_process_monthly_departures',
            'can_view_employees',
            'can_add_employees',
            'can_edit_employees',
            'can_delete_employees',
            'can_view_leaves',
            'can_add_leaves',
            'can_edit_leaves',
            'can_delete_leaves',
            'can_approve_leaves',
            'can_view_departures',
            'can_add_departures',
            'can_edit_departures',
            'can_delete_departures',
            'can_convert_departures',
            'can_view_leave_reports',
            'can_view_departure_reports',
            'can_export_employees',
            'can_export_leaves',
            'can_export_departures',
            'can_export_balances',
            'can_export_reports',
            'can_view_statistics',
            'can_view_own_school_only',
            'can_manage_school_assignments'
        ]
        
        # التحقق من الأعمدة الموجودة
        cursor.execute("PRAGMA table_info(user)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        
        # إضافة الأعمدة المفقودة
        added_count = 0
        for column in new_columns:
            if column not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE user ADD COLUMN {column} BOOLEAN DEFAULT 0")
                    added_count += 1
                    print(f"✅ تم إضافة العمود: {column}")
                except sqlite3.Error as e:
                    print(f"⚠️ خطأ في إضافة العمود {column}: {e}")
        
        print(f"📊 تم إضافة {added_count} عمود جديد")
        
        # تحديث صلاحيات المدراء
        cursor.execute("SELECT id FROM user WHERE is_admin = 1")
        admin_users = cursor.fetchall()
        
        if admin_users:
            # إنشاء قائمة بجميع الأعمدة للتحديث
            update_columns = ', '.join([f"{col} = 1" for col in new_columns])
            cursor.execute(f"UPDATE user SET {update_columns} WHERE is_admin = 1")
            print(f"✅ تم تحديث صلاحيات {len(admin_users)} مدير")
        
        # حفظ التغييرات
        conn.commit()
        print("✅ تم حفظ جميع التغييرات بنجاح")
        
        # إحصائيات نهائية
        cursor.execute("SELECT COUNT(*) FROM user")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM user WHERE is_admin = 1")
        admin_count = cursor.fetchone()[0]
        
        print(f"\n📈 إحصائيات قاعدة البيانات:")
        print(f"   - إجمالي المستخدمين: {total_users}")
        print(f"   - المدراء: {admin_count}")
        print(f"   - المستخدمين العاديين: {total_users - admin_count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ خطأ في ترحيل قاعدة البيانات: {e}")
        return False

if __name__ == '__main__':
    print("🚀 بدء عملية ترحيل قاعدة البيانات...")
    success = migrate_database()
    
    if success:
        print("\n🎉 تم ترحيل قاعدة البيانات بنجاح!")
        print("يمكنك الآن تشغيل التطبيق باستخدام: python app.py")
    else:
        print("\n❌ فشل في ترحيل قاعدة البيانات")
        print("يرجى التحقق من الأخطاء أعلاه وإعادة المحاولة")