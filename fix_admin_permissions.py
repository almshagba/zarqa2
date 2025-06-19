#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت سريع لاستعادة صلاحيات المدير
"""

import sqlite3
import os

def fix_admin_permissions():
    """استعادة صلاحيات المدير"""
    db_path = 'instance/employees.db'
    
    if not os.path.exists(db_path):
        print(f"قاعدة البيانات غير موجودة: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("بدء استعادة صلاحيات المدير...")
        
        # التحقق من المدراء الموجودين
        cursor.execute("SELECT id, username FROM user WHERE is_admin = 1")
        admins = cursor.fetchall()
        
        if not admins:
            print("لا يوجد مدراء في النظام")
            return False
        
        print(f"تم العثور على {len(admins)} مدير")
        
        # الحصول على أعمدة الجدول
        cursor.execute("PRAGMA table_info(user)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # قائمة الصلاحيات
        permissions = [
            'can_backup_database', 'can_view_employees_list', 'can_view_employee_details',
            'can_edit_employees_data', 'can_add_new_employee', 'can_delete_employee',
            'can_view_schools_list', 'can_view_school_details', 'can_edit_schools_data',
            'can_add_new_school', 'can_delete_school', 'can_view_leaves_list',
            'can_view_leave_details', 'can_edit_leaves_data', 'can_add_new_leave',
            'can_delete_leave', 'can_manage_leave_balances', 'can_view_departures_list',
            'can_view_departure_details', 'can_edit_departures_data', 'can_add_new_departure',
            'can_delete_departure', 'can_view_transfers_list', 'can_view_transfer_details',
            'can_edit_transfers_data', 'can_add_new_transfer', 'can_delete_transfer',
            'can_view_employee_reports', 'can_view_school_reports', 'can_view_comprehensive_reports',
            'can_export_employee_data', 'can_export_school_data', 'can_export_report_data',
            'can_view_users_list', 'can_add_new_user', 'can_manage_user_permissions'
        ]
        
        # فلترة الصلاحيات الموجودة
        valid_permissions = [p for p in permissions if p in columns]
        
        if not valid_permissions:
            print("لا توجد أعمدة صلاحيات صالحة")
            return False
        
        # تحديث الصلاحيات
        updates = ', '.join([f"{p} = 1" for p in valid_permissions])
        query = f"UPDATE user SET {updates} WHERE is_admin = 1"
        
        cursor.execute(query)
        conn.commit()
        
        print(f"تم تحديث {len(valid_permissions)} صلاحية")
        print(f"تم تحديث {len(admins)} مدير")
        
        # التحقق من النتيجة
        for admin_id, username in admins:
            print(f"المدير: {username} - تم تحديث الصلاحيات")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"خطأ: {e}")
        return False

if __name__ == '__main__':
    print("استعادة صلاحيات المدير...")
    if fix_admin_permissions():
        print("\nتم بنجاح! المدير لديه الآن جميع الصلاحيات")
    else:
        print("\nفشل في استعادة الصلاحيات")
    
    input("\nاضغط Enter للخروج...")