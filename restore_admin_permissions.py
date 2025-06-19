# -*- coding: utf-8 -*-
"""
سكريبت لاستعادة جميع الصلاحيات للمدير
"""

import sqlite3
import os

def restore_admin_permissions():
    """استعادة جميع الصلاحيات للمدير"""
    db_path = 'instance/employees.db'
    
    if not os.path.exists(db_path):
        print(f"❌ لم يتم العثور على قاعدة البيانات: {db_path}")
        return False
    
    try:
        # الاتصال بقاعدة البيانات
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 بدء استعادة صلاحيات المدير...")
        
        # قائمة جميع أعمدة الصلاحيات
        permission_columns = [
            'can_backup_database',
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
        
        # التحقق من وجود المدراء
        cursor.execute("SELECT id, username FROM user WHERE is_admin = 1")
        admin_users = cursor.fetchall()
        
        if not admin_users:
            print("❌ لم يتم العثور على أي مدراء في النظام")
            return False
        
        print(f"📋 تم العثور على {len(admin_users)} مدير:")
        for admin_id, username in admin_users:
            print(f"   - {username} (ID: {admin_id})")
        
        # التحقق من الأعمدة الموجودة في الجدول
        cursor.execute("PRAGMA table_info(user)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        
        # فلترة الأعمدة الموجودة فقط
        valid_columns = [col for col in permission_columns if col in existing_columns]
        missing_columns = [col for col in permission_columns if col not in existing_columns]
        
        if missing_columns:
            print(f"⚠️ الأعمدة التالية غير موجودة في قاعدة البيانات: {len(missing_columns)} عمود")
            for col in missing_columns[:5]:  # عرض أول 5 أعمدة فقط
                print(f"   - {col}")
            if len(missing_columns) > 5:
                print(f"   ... و {len(missing_columns) - 5} أعمدة أخرى")
        
        if not valid_columns:
            print("❌ لم يتم العثور على أي أعمدة صلاحيات صالحة")
            return False
        
        # تحديث صلاحيات جميع المدراء
        update_columns = ', '.join([f"{col} = 1" for col in valid_columns])
        cursor.execute(f"UPDATE user SET {update_columns} WHERE is_admin = 1")
        
        # حفظ التغييرات
        conn.commit()
        
        print(f"✅ تم تحديث {len(valid_columns)} صلاحية لجميع المدراء")
        print(f"📊 تم تحديث صلاحيات {len(admin_users)} مدير بنجاح")
        
        # التحقق من النتائج
        cursor.execute("SELECT username, COUNT(*) as permissions_count FROM user WHERE is_admin = 1")
        result = cursor.fetchone()
        
        print(f"\n🎉 تم استعادة جميع الصلاحيات بنجاح!")
        print(f"📈 إحصائيات:")
        print(f"   - عدد الصلاحيات المحدثة: {len(valid_columns)}")
        print(f"   - عدد المدراء المحدثين: {len(admin_users)}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ خطأ في استعادة صلاحيات المدير: {e}")
        return False

if __name__ == '__main__':
    print("🚀 بدء عملية استعادة صلاحيات المدير...")
    success = restore_admin_permissions()
    
    if success:
        print("\n✅ تم استعادة جميع صلاحيات المدير بنجاح!")
        print("يمكن للمدير الآن الوصول إلى جميع وظائف النظام")
    else:
        print("\n❌ فشل في استعادة صلاحيات المدير")
        print("يرجى التحقق من الأخطاء أعلاه وإعادة المحاولة")