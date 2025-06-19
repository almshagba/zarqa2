#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
فحص شامل لنظام إدارة الموظفين وإصلاح مشاكل الصلاحيات
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash

def comprehensive_system_check():
    """
    فحص شامل للنظام وإصلاح جميع مشاكل الصلاحيات
    """
    
    # مسار قاعدة البيانات
    db_path = os.path.join('instance', 'employees.db')
    
    if not os.path.exists(db_path):
        print("❌ خطأ: لم يتم العثور على قاعدة البيانات")
        print(f"المسار المتوقع: {os.path.abspath(db_path)}")
        return False
    
    try:
        # الاتصال بقاعدة البيانات
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 بدء الفحص الشامل للنظام...")
        print("=" * 50)
        
        # 1. فحص جدول المستخدمين
        print("\n📋 فحص جدول المستخدمين:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")
        if not cursor.fetchone():
            print("❌ جدول المستخدمين غير موجود!")
            return False
        
        # 2. فحص المستخدمين الموجودين
        cursor.execute("SELECT id, username, full_name, is_admin FROM user")
        users = cursor.fetchall()
        
        print(f"👥 عدد المستخدمين في النظام: {len(users)}")
        for user in users:
            user_id, username, full_name, is_admin = user
            admin_status = "مدير" if is_admin else "مستخدم عادي"
            print(f"   - {username} ({full_name}) - {admin_status}")
        
        # 3. فحص أعمدة الصلاحيات
        print("\n🔐 فحص أعمدة الصلاحيات:")
        cursor.execute("PRAGMA table_info(user)")
        columns = cursor.fetchall()
        
        permission_columns = []
        for column in columns:
            column_name = column[1]
            if column_name.startswith('can_') or column_name == 'is_admin':
                permission_columns.append(column_name)
        
        print(f"📊 عدد أعمدة الصلاحيات الموجودة: {len(permission_columns)}")
        
        # قائمة الصلاحيات المطلوبة
        required_permissions = [
            'is_admin',
            'can_backup_database',
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
            'can_manage_system_settings',
            'can_process_monthly_departures',
            # صلاحيات مفصلة إضافية
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
            'can_manage_school_employees',
            'can_view_school_statistics'
        ]
        
        # 4. إضافة الأعمدة المفقودة
        missing_permissions = []
        for perm in required_permissions:
            if perm not in permission_columns:
                missing_permissions.append(perm)
        
        if missing_permissions:
            print(f"⚠️  أعمدة صلاحيات مفقودة: {len(missing_permissions)}")
            print("🔧 إضافة الأعمدة المفقودة...")
            
            for perm in missing_permissions:
                try:
                    if perm == 'is_admin':
                        cursor.execute(f"ALTER TABLE user ADD COLUMN {perm} BOOLEAN DEFAULT 0")
                    else:
                        cursor.execute(f"ALTER TABLE user ADD COLUMN {perm} BOOLEAN DEFAULT 0")
                    print(f"   ✅ تم إضافة عمود: {perm}")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" not in str(e):
                        print(f"   ❌ خطأ في إضافة عمود {perm}: {e}")
        else:
            print("✅ جميع أعمدة الصلاحيات موجودة")
        
        # 5. إصلاح صلاحيات جميع المستخدمين
        print("\n🛠️  إصلاح صلاحيات المستخدمين:")
        
        # الحصول على قائمة محدثة بالأعمدة
        cursor.execute("PRAGMA table_info(user)")
        columns = cursor.fetchall()
        current_permission_columns = [col[1] for col in columns if col[1].startswith('can_') or col[1] == 'is_admin']
        
        # إصلاح كل مستخدم
        for user in users:
            user_id, username, full_name, is_admin = user
            
            print(f"\n👤 إصلاح صلاحيات المستخدم: {username}")
            
            # إذا كان مدير، منح جميع الصلاحيات
            if is_admin or username in ['admin', 'wael']:
                # تأكد من أن is_admin = 1
                cursor.execute("UPDATE user SET is_admin = 1 WHERE id = ?", (user_id,))
                
                # منح جميع الصلاحيات
                update_parts = []
                for perm in current_permission_columns:
                    if perm != 'is_admin':
                        update_parts.append(f"{perm} = 1")
                
                if update_parts:
                    update_query = f"UPDATE user SET {', '.join(update_parts)} WHERE id = ?"
                    cursor.execute(update_query, (user_id,))
                    print(f"   ✅ تم منح جميع الصلاحيات ({len(update_parts)} صلاحية)")
            else:
                # للمستخدمين العاديين، منح صلاحيات أساسية
                basic_permissions = [
                    'can_view_employees_list',
                    'can_view_employee_details',
                    'can_view_schools_list',
                    'can_view_school_details',
                    'can_view_leaves_list',
                    'can_view_leave_details'
                ]
                
                update_parts = []
                for perm in basic_permissions:
                    if perm in current_permission_columns:
                        update_parts.append(f"{perm} = 1")
                
                if update_parts:
                    update_query = f"UPDATE user SET {', '.join(update_parts)} WHERE id = ?"
                    cursor.execute(update_query, (user_id,))
                    print(f"   ✅ تم منح الصلاحيات الأساسية ({len(update_parts)} صلاحية)")
        
        # 6. التحقق من النتائج النهائية
        print("\n📊 التحقق من النتائج النهائية:")
        
        for user in users:
            user_id, username, full_name, is_admin = user
            
            # عد الصلاحيات الممنوحة
            permission_count_query = "SELECT " + ", ".join([f"COALESCE({perm}, 0)" for perm in current_permission_columns if perm != 'is_admin']) + " FROM user WHERE id = ?"
            cursor.execute(permission_count_query, (user_id,))
            permissions = cursor.fetchone()
            granted_count = sum(permissions) if permissions else 0
            
            # التحقق من حالة المدير
            cursor.execute("SELECT is_admin FROM user WHERE id = ?", (user_id,))
            admin_status = cursor.fetchone()[0]
            
            status = "مدير" if admin_status else "مستخدم عادي"
            print(f"   👤 {username}: {status} - {granted_count} صلاحية ممنوحة")
        
        # حفظ التغييرات
        conn.commit()
        
        print("\n" + "=" * 50)
        print("✅ تم إكمال الفحص والإصلاح بنجاح!")
        print("\n📋 ملخص الإصلاحات:")
        print(f"   - تم فحص {len(users)} مستخدم")
        print(f"   - تم إضافة {len(missing_permissions)} عمود صلاحيات مفقود")
        print(f"   - تم إصلاح صلاحيات جميع المستخدمين")
        
        print("\n🔐 بيانات تسجيل الدخول:")
        print("   المدير: admin / admin123")
        print("   وائل: wael / 123456")
        
        print("\n⚠️  تعليمات مهمة:")
        print("   1. أغلق التطبيق تماماً قبل تشغيل هذا السكريبت")
        print("   2. أعد تشغيل التطبيق بعد تشغيل هذا السكريبت")
        print("   3. تأكد من تسجيل الدخول بحساب المدير أو وائل")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في الفحص: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    try:
        print("🚀 بدء الفحص الشامل لنظام إدارة الموظفين")
        print("=" * 60)
        
        success = comprehensive_system_check()
        
        if success:
            print("\n🎉 تم إصلاح جميع مشاكل النظام بنجاح!")
        else:
            print("\n❌ فشل في إصلاح النظام")
            
    except Exception as e:
        print(f"❌ خطأ عام: {e}")
    
    input("\nاضغط Enter للخروج...")