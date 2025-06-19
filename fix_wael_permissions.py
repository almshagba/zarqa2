#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت إصلاح صلاحيات المستخدم wael
"""

import sqlite3
import os

def fix_wael_permissions():
    """إصلاح صلاحيات المستخدم wael"""
    db_path = 'instance/employees.db'
    
    if not os.path.exists(db_path):
        print(f"❌ قاعدة البيانات غير موجودة: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 فحص المستخدم wael...")
        
        # البحث عن المستخدم wael
        cursor.execute("SELECT id, username, is_admin FROM user WHERE username = 'wael'")
        wael_user = cursor.fetchone()
        
        if not wael_user:
            print("❌ المستخدم wael غير موجود في النظام")
            print("يرجى إنشاء المستخدم أولاً باستخدام create_user_wael.py")
            return False
        
        user_id, username, is_admin = wael_user
        print(f"✅ تم العثور على المستخدم: {username} (ID: {user_id})")
        print(f"حالة المدير الحالية: {'نعم' if is_admin else 'لا'}")
        
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
        
        print(f"✅ الصلاحيات الموجودة في قاعدة البيانات: {len(existing_permissions)}")
        if missing_permissions:
            print(f"⚠️ الصلاحيات المفقودة من قاعدة البيانات: {len(missing_permissions)}")
            for perm in missing_permissions[:3]:  # عرض أول 3 فقط
                print(f"   - {perm}")
            if len(missing_permissions) > 3:
                print(f"   ... و {len(missing_permissions) - 3} صلاحية أخرى")
        
        # فحص الصلاحيات الحالية للمستخدم wael
        if existing_permissions:
            permission_columns = ', '.join(existing_permissions)
            query = f"SELECT {permission_columns} FROM user WHERE username = 'wael'"
            cursor.execute(query)
            current_permissions = cursor.fetchone()
            
            if current_permissions:
                granted_count = sum(1 for perm in current_permissions if perm == 1)
                denied_count = len(current_permissions) - granted_count
                
                print(f"📊 الصلاحيات الحالية للمستخدم wael:")
                print(f"   ✅ مُمنوحة: {granted_count}")
                print(f"   ❌ مرفوضة: {denied_count}")
                
                if denied_count > 0:
                    print("\n🔧 تحديث جميع الصلاحيات...")
                    
                    # تحديث جميع الصلاحيات إلى 1
                    updates = ', '.join([f"{perm} = 1" for perm in existing_permissions])
                    update_query = f"UPDATE user SET is_admin = 1, {updates} WHERE username = 'wael'"
                    cursor.execute(update_query)
                    
                    print(f"✅ تم تحديث {len(existing_permissions)} صلاحية للمستخدم wael")
                else:
                    print("✅ جميع الصلاحيات مُمنوحة بالفعل")
                    # التأكد من أن المستخدم مدير
                    cursor.execute("UPDATE user SET is_admin = 1 WHERE username = 'wael'")
        else:
            print("❌ لا توجد أعمدة صلاحيات في قاعدة البيانات")
            # على الأقل تعيينه كمدير
            cursor.execute("UPDATE user SET is_admin = 1 WHERE username = 'wael'")
            print("✅ تم تعيين المستخدم wael كمدير")
        
        # حفظ التغييرات
        conn.commit()
        
        # التحقق من النتيجة النهائية
        cursor.execute("SELECT username, is_admin FROM user WHERE username = 'wael'")
        result = cursor.fetchone()
        
        if result:
            username, is_admin = result
            print(f"\n🎉 النتيجة النهائية:")
            print(f"   المستخدم: {username}")
            print(f"   مدير: {'نعم' if is_admin else 'لا'}")
            
            # فحص الصلاحيات مرة أخرى
            if existing_permissions:
                permission_columns = ', '.join(existing_permissions)
                query = f"SELECT {permission_columns} FROM user WHERE username = 'wael'"
                cursor.execute(query)
                final_permissions = cursor.fetchone()
                
                if final_permissions:
                    final_granted = sum(1 for perm in final_permissions if perm == 1)
                    print(f"   الصلاحيات المُمنوحة: {final_granted}/{len(existing_permissions)}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False

if __name__ == '__main__':
    print("🚀 بدء إصلاح صلاحيات المستخدم wael...")
    print("=" * 50)
    
    success = fix_wael_permissions()
    
    print("=" * 50)
    if success:
        print("✅ تم بنجاح! المستخدم wael لديه الآن جميع الصلاحيات")
        print("يمكن الآن تسجيل الدخول والوصول لجميع الوظائف")
    else:
        print("❌ فشل في إصلاح الصلاحيات")
        print("يرجى التحقق من الأخطاء أعلاه")
    
    print("\nاضغط Enter للخروج...")
    input()