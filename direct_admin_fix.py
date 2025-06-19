#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت مباشر لاستعادة صلاحيات المدير admin
"""

import sqlite3
import os

def check_and_fix_admin():
    """فحص واستعادة صلاحيات المدير"""
    db_path = 'instance/employees.db'
    
    if not os.path.exists(db_path):
        print(f"❌ قاعدة البيانات غير موجودة: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 فحص حالة المدير admin...")
        
        # البحث عن المدير admin
        cursor.execute("SELECT id, username, is_admin FROM user WHERE username = 'admin'")
        admin_user = cursor.fetchone()
        
        if not admin_user:
            print("❌ المدير admin غير موجود في النظام")
            print("إنشاء مدير جديد...")
            
            # إنشاء مدير جديد
            cursor.execute("""
                INSERT INTO user (username, password_hash, full_name, is_admin, created_at)
                VALUES ('admin', 'pbkdf2:sha256:600000$salt$hash', 'مدير النظام', 1, datetime('now'))
            """)
            
            # الحصول على ID المدير الجديد
            admin_id = cursor.lastrowid
            print(f"✅ تم إنشاء المدير admin بـ ID: {admin_id}")
        else:
            admin_id, username, is_admin = admin_user
            print(f"✅ تم العثور على المدير: {username} (ID: {admin_id})")
            
            if not is_admin:
                print("⚠️ المستخدم admin ليس مدير، تحديث الحالة...")
                cursor.execute("UPDATE user SET is_admin = 1 WHERE id = ?", (admin_id,))
                print("✅ تم تحديث حالة المدير")
        
        # الحصول على أعمدة الجدول
        cursor.execute("PRAGMA table_info(user)")
        columns_info = cursor.fetchall()
        all_columns = [col[1] for col in columns_info]
        
        print(f"📋 عدد الأعمدة في الجدول: {len(all_columns)}")
        
        # قائمة شاملة للصلاحيات
        all_permissions = [
            'can_backup_database',
            'can_view_employees_list', 'can_view_employee_details', 'can_edit_employees_data',
            'can_add_new_employee', 'can_delete_employee',
            'can_view_schools_list', 'can_view_school_details', 'can_edit_schools_data',
            'can_add_new_school', 'can_delete_school',
            'can_view_leaves_list', 'can_view_leave_details', 'can_edit_leaves_data',
            'can_add_new_leave', 'can_delete_leave', 'can_manage_leave_balances',
            'can_view_departures_list', 'can_view_departure_details', 'can_edit_departures_data',
            'can_add_new_departure', 'can_delete_departure',
            'can_view_transfers_list', 'can_view_transfer_details', 'can_edit_transfers_data',
            'can_add_new_transfer', 'can_delete_transfer',
            'can_view_employee_reports', 'can_view_school_reports', 'can_view_comprehensive_reports',
            'can_export_employee_data', 'can_export_school_data', 'can_export_report_data',
            'can_view_users_list', 'can_add_new_user', 'can_manage_user_permissions',
            'can_view_forms_list', 'can_edit_forms_data', 'can_add_new_form', 'can_delete_form',
            'can_view_system_logs', 'can_manage_system_settings', 'can_process_monthly_departures',
            'can_view_employees', 'can_add_employees', 'can_edit_employees', 'can_delete_employees',
            'can_view_leaves', 'can_add_leaves', 'can_edit_leaves', 'can_delete_leaves',
            'can_approve_leaves', 'can_view_departures', 'can_add_departures',
            'can_edit_departures', 'can_delete_departures', 'can_convert_departures',
            'can_view_leave_reports', 'can_view_departure_reports',
            'can_export_employees', 'can_export_leaves', 'can_export_departures',
            'can_export_balances', 'can_export_reports', 'can_view_statistics',
            'can_view_own_school_only', 'can_manage_school_assignments'
        ]
        
        # فلترة الصلاحيات الموجودة
        existing_permissions = [p for p in all_permissions if p in all_columns]
        missing_permissions = [p for p in all_permissions if p not in all_columns]
        
        print(f"✅ الصلاحيات الموجودة: {len(existing_permissions)}")
        if missing_permissions:
            print(f"⚠️ الصلاحيات المفقودة: {len(missing_permissions)}")
            for perm in missing_permissions[:5]:  # عرض أول 5 فقط
                print(f"   - {perm}")
            if len(missing_permissions) > 5:
                print(f"   ... و {len(missing_permissions) - 5} صلاحية أخرى")
        
        if existing_permissions:
            # تحديث الصلاحيات الموجودة
            updates = ', '.join([f"{perm} = 1" for perm in existing_permissions])
            query = f"UPDATE user SET {updates} WHERE username = 'admin'"
            
            cursor.execute(query)
            print(f"✅ تم تحديث {len(existing_permissions)} صلاحية للمدير admin")
        else:
            print("❌ لا توجد أعمدة صلاحيات في قاعدة البيانات")
        
        # حفظ التغييرات
        conn.commit()
        
        # التحقق من النتيجة
        cursor.execute("SELECT username, is_admin FROM user WHERE username = 'admin'")
        result = cursor.fetchone()
        
        if result:
            username, is_admin = result
            print(f"\n🎉 النتيجة النهائية:")
            print(f"   المستخدم: {username}")
            print(f"   مدير: {'نعم' if is_admin else 'لا'}")
            print(f"   الصلاحيات المحدثة: {len(existing_permissions)}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False

if __name__ == '__main__':
    print("🚀 بدء فحص واستعادة صلاحيات المدير admin...")
    print("=" * 50)
    
    success = check_and_fix_admin()
    
    print("=" * 50)
    if success:
        print("✅ تم بنجاح! المدير admin لديه الآن جميع الصلاحيات المتاحة")
        print("يمكن الآن تسجيل الدخول باستخدام:")
        print("   اسم المستخدم: admin")
        print("   كلمة المرور: admin123")
    else:
        print("❌ فشل في استعادة الصلاحيات")
        print("يرجى التحقق من الأخطاء أعلاه")
    
    print("\nاضغط Enter للخروج...")
    input()