#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت تحديث قاعدة البيانات لإضافة الصلاحيات المنظمة الجديدة
يجب تشغيل هذا السكريبت مرة واحدة فقط لتحديث قاعدة البيانات الموجودة
"""

import sqlite3
import os
from datetime import datetime

def update_database():
    """تحديث قاعدة البيانات لإضافة الصلاحيات الجديدة"""
    
    # مسار قاعدة البيانات
    db_path = 'employees.db'
    
    if not os.path.exists(db_path):
        print(f"خطأ: لم يتم العثور على قاعدة البيانات في المسار: {db_path}")
        return False
    
    try:
        # الاتصال بقاعدة البيانات
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("بدء تحديث قاعدة البيانات...")
        
        # قائمة الأعمدة الجديدة للصلاحيات
        new_permission_columns = [
            # Employee permissions
            'can_view_employees_list',
            'can_view_employee_details', 
            'can_edit_employees_data',
            'can_add_new_employee',
            'can_delete_employee',
            
            # School permissions
            'can_view_schools_list',
            'can_view_school_details',
            'can_edit_schools_data', 
            'can_add_new_school',
            'can_delete_school',
            
            # Leave permissions
            'can_view_leaves_list',
            'can_view_leave_details',
            'can_edit_leaves_data',
            'can_add_new_leave', 
            'can_delete_leave',
            'can_manage_leave_balances',
            
            # Departure permissions
            'can_view_departures_list',
            'can_view_departure_details',
            'can_edit_departures_data',
            'can_add_new_departure',
            'can_delete_departure',
            
            # Transfer permissions
            'can_view_transfers_list',
            'can_view_transfer_details', 
            'can_edit_transfers_data',
            'can_add_new_transfer',
            'can_delete_transfer',
            
            # Report permissions
            'can_view_employee_reports',
            'can_view_school_reports',
            'can_view_comprehensive_reports',
            
            # Export permissions
            'can_export_employee_data',
            'can_export_school_data',
            'can_export_report_data',
            
            # User management permissions
            'can_view_users_list',
            'can_add_new_user',
            'can_manage_user_permissions',
            
            # Form permissions
            'can_view_forms_list',
            'can_edit_forms_data',
            'can_add_new_form',
            'can_delete_form',
            
            # System permissions
            'can_view_system_logs',
            'can_manage_system_settings'
        ]
        
        # التحقق من الأعمدة الموجودة في جدول user
        cursor.execute("PRAGMA table_info(user)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        
        # إضافة الأعمدة الجديدة
        columns_added = 0
        for column in new_permission_columns:
            if column not in existing_columns:
                try:
                    sql = f"ALTER TABLE user ADD COLUMN {column} BOOLEAN DEFAULT 0"
                    cursor.execute(sql)
                    print(f"تم إضافة العمود: {column}")
                    columns_added += 1
                except sqlite3.Error as e:
                    print(f"خطأ في إضافة العمود {column}: {e}")
            else:
                print(f"العمود {column} موجود بالفعل")
        
        # تحديث صلاحيات المديرين الموجودين
        print("\nتحديث صلاحيات المديرين الموجودين...")
        
        # الحصول على قائمة المديرين
        cursor.execute("SELECT id, username FROM user WHERE is_admin = 1")
        admins = cursor.fetchall()
        
        if admins:
            # إنشاء قائمة بجميع الأعمدة الجديدة لتحديثها
            update_columns = ', '.join([f"{col} = 1" for col in new_permission_columns])
            
            for admin_id, username in admins:
                try:
                    sql = f"UPDATE user SET {update_columns} WHERE id = ?"
                    cursor.execute(sql, (admin_id,))
                    print(f"تم تحديث صلاحيات المدير: {username}")
                except sqlite3.Error as e:
                    print(f"خطأ في تحديث صلاحيات المدير {username}: {e}")
        
        # حفظ التغييرات
        conn.commit()
        
        print(f"\nتم تحديث قاعدة البيانات بنجاح!")
        print(f"تم إضافة {columns_added} عمود جديد")
        print(f"تم تحديث صلاحيات {len(admins)} مدير")
        
        # إنشاء نسخة احتياطية
        backup_path = f"employees_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        cursor.execute(f"VACUUM INTO '{backup_path}'")
        print(f"تم إنشاء نسخة احتياطية: {backup_path}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"خطأ في قاعدة البيانات: {e}")
        return False
    except Exception as e:
        print(f"خطأ عام: {e}")
        return False
    finally:
        if conn:
            conn.close()

def verify_update():
    """التحقق من نجاح التحديث"""
    try:
        conn = sqlite3.connect('employees.db')
        cursor = conn.cursor()
        
        # التحقق من الأعمدة الجديدة
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        new_columns = [col for col in columns if col.startswith('can_view_') or 
                      col.startswith('can_edit_') or col.startswith('can_add_') or 
                      col.startswith('can_delete_') or col.startswith('can_manage_') or
                      col.startswith('can_export_')]
        
        print(f"\nالأعمدة الجديدة المضافة ({len(new_columns)}):")
        for col in sorted(new_columns):
            print(f"  - {col}")
        
        # التحقق من عدد المستخدمين
        cursor.execute("SELECT COUNT(*) FROM user")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM user WHERE is_admin = 1")
        admin_count = cursor.fetchone()[0]
        
        print(f"\nإحصائيات المستخدمين:")
        print(f"  - إجمالي المستخدمين: {user_count}")
        print(f"  - عدد المديرين: {admin_count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"خطأ في التحقق: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("سكريبت تحديث الصلاحيات المنظمة")
    print("=" * 60)
    
    # تأكيد من المستخدم
    response = input("\nهل تريد المتابعة مع تحديث قاعدة البيانات؟ (y/n): ")
    
    if response.lower() in ['y', 'yes', 'نعم']:
        success = update_database()
        
        if success:
            print("\n" + "=" * 60)
            print("التحقق من التحديث:")
            print("=" * 60)
            verify_update()
            
            print("\n" + "=" * 60)
            print("تم التحديث بنجاح! يمكنك الآن استخدام النظام الجديد للصلاحيات.")
            print("تأكد من إعادة تشغيل التطبيق لتطبيق التغييرات.")
            print("=" * 60)
        else:
            print("\nفشل في تحديث قاعدة البيانات. يرجى مراجعة الأخطاء أعلاه.")
    else:
        print("تم إلغاء التحديث.")