#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إصلاح شامل لجميع مشاكل النظام والصلاحيات
"""

import sqlite3
import os
import shutil
from datetime import datetime
from werkzeug.security import generate_password_hash

def complete_system_fix():
    """
    إصلاح شامل لجميع مشاكل النظام
    """
    
    print("🚀 بدء الإصلاح الشامل لنظام إدارة الموظفين")
    print("=" * 60)
    
    # الخطوة 1: إصلاح دالة has_permission
    print("\n🔧 الخطوة 1: إصلاح دالة has_permission")
    if not fix_has_permission_function():
        print("❌ فشل في إصلاح دالة has_permission")
        return False
    
    # الخطوة 2: إصلاح قاعدة البيانات والصلاحيات
    print("\n🔧 الخطوة 2: إصلاح قاعدة البيانات والصلاحيات")
    if not fix_database_permissions():
        print("❌ فشل في إصلاح قاعدة البيانات")
        return False
    
    print("\n🎉 تم إكمال الإصلاح الشامل بنجاح!")
    return True

def fix_has_permission_function():
    """
    إصلاح دالة has_permission في ملف models.py
    """
    
    models_file = 'models.py'
    
    if not os.path.exists(models_file):
        print("❌ خطأ: ملف models.py غير موجود")
        return False
    
    try:
        # إنشاء نسخة احتياطية
        backup_file = f'models_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py'
        shutil.copy2(models_file, backup_file)
        print(f"✅ تم إنشاء نسخة احتياطية: {backup_file}")
        
        # قراءة الملف الحالي
        with open(models_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # البحث عن دالة has_permission الحالية وإزالتها
        start_marker = "def has_permission(self, permission):"
        
        start_index = content.find(start_marker)
        if start_index == -1:
            print("❌ لم يتم العثور على دالة has_permission")
            return False
        
        # البحث عن نهاية الدالة
        lines = content[start_index:].split('\n')
        end_line_index = 0
        indent_level = None
        
        for i, line in enumerate(lines):
            if i == 0:  # السطر الأول (def has_permission)
                continue
            
            if line.strip() == "":
                continue
                
            if indent_level is None and line.strip():
                # تحديد مستوى المسافة البادئة للدالة
                indent_level = len(line) - len(line.lstrip())
                continue
            
            if line.strip() and indent_level is not None:
                current_indent = len(line) - len(line.lstrip())
                if current_indent <= indent_level and not line.strip().startswith('"""') and not line.strip().startswith("'''"):
                    # وصلنا لنهاية الدالة
                    end_line_index = i
                    break
        
        if end_line_index == 0:
            # إذا لم نجد نهاية واضحة، نبحث عن الدالة التالية
            next_def_index = content.find('\n    def ', start_index + 1)
            if next_def_index != -1:
                end_index = next_def_index
            else:
                end_index = len(content)
        else:
            # حساب الفهرس الفعلي في النص الكامل
            end_index = start_index + sum(len(line) + 1 for line in lines[:end_line_index])
        
        # إزالة الدالة القديمة
        before_function = content[:start_index]
        after_function = content[end_index:]
        
        # الدالة الجديدة المحسنة
        new_function = '''    def has_permission(self, permission=None):
        """Return a dictionary of all permissions or check specific permission"""
        if self.is_admin:
            # المدير لديه جميع الصلاحيات
            if permission:
                return True
            else:
                # إرجاع قاموس بجميع الصلاحيات للمدير
                all_permissions = {}
                # جميع الصلاحيات الأساسية
                basic_perms = [
                    'view_employees_list', 'view_employee_details', 'edit_employees_data', 'add_new_employee', 'delete_employee',
                    'view_schools_list', 'view_school_details', 'edit_schools_data', 'add_new_school', 'delete_school',
                    'view_leaves_list', 'view_leave_details', 'edit_leaves_data', 'add_new_leave', 'delete_leave',
                    'manage_leave_balances', 'view_departures_list', 'view_departure_details', 'edit_departures_data',
                    'add_new_departure', 'delete_departure', 'view_transfers_list', 'view_transfer_details',
                    'edit_transfers_data', 'add_new_transfer', 'delete_transfer', 'view_employee_reports',
                    'view_school_reports', 'view_comprehensive_reports', 'export_employee_data', 'export_school_data',
                    'export_report_data', 'view_users_list', 'add_new_user', 'manage_user_permissions',
                    'view_forms_list', 'edit_forms_data', 'add_new_form', 'delete_form', 'view_system_logs',
                    'backup_database', 'manage_system_settings', 'process_monthly_departures',
                    # الصلاحيات المستخدمة في القوالب
                    'can_view_employees', 'can_manage_employees', 'can_manage_schools', 'can_manage_transfers',
                    'can_view_leaves', 'can_manage_leaves', 'can_view_departures', 'can_manage_departures',
                    'can_manage_leave_balances', 'can_view_reports', 'can_view_employee_reports',
                    'can_view_school_reports', 'can_view_leave_reports', 'can_view_departure_reports',
                    'can_view_comprehensive_reports', 'can_manage_forms', 'view_users', 'edit_users',
                    'view_employees', 'edit_employees', 'manage_user_permissions'
                ]
                for perm in basic_perms:
                    all_permissions[perm] = True
                return all_permissions
        
        # للمستخدمين العاديين
        permission_map = {
            # Employee permissions
            'view_employees_list': getattr(self, 'can_view_employees_list', False),
            'view_employee_details': getattr(self, 'can_view_employee_details', False),
            'edit_employees_data': getattr(self, 'can_edit_employees_data', False),
            'add_new_employee': getattr(self, 'can_add_new_employee', False),
            'delete_employee': getattr(self, 'can_delete_employee', False),
            
            # School permissions
            'view_schools_list': getattr(self, 'can_view_schools_list', False),
            'view_school_details': getattr(self, 'can_view_school_details', False),
            'edit_schools_data': getattr(self, 'can_edit_schools_data', False),
            'add_new_school': getattr(self, 'can_add_new_school', False),
            'delete_school': getattr(self, 'can_delete_school', False),
            
            # Leave permissions
            'view_leaves_list': getattr(self, 'can_view_leaves_list', False),
            'view_leave_details': getattr(self, 'can_view_leave_details', False),
            'edit_leaves_data': getattr(self, 'can_edit_leaves_data', False),
            'add_new_leave': getattr(self, 'can_add_new_leave', False),
            'delete_leave': getattr(self, 'can_delete_leave', False),
            'manage_leave_balances': getattr(self, 'can_manage_leave_balances', False),
            
            # Departure permissions
            'view_departures_list': getattr(self, 'can_view_departures_list', False),
            'view_departure_details': getattr(self, 'can_view_departure_details', False),
            'edit_departures_data': getattr(self, 'can_edit_departures_data', False),
            'add_new_departure': getattr(self, 'can_add_new_departure', False),
            'delete_departure': getattr(self, 'can_delete_departure', False),
            
            # Transfer permissions
            'view_transfers_list': getattr(self, 'can_view_transfers_list', False),
            'view_transfer_details': getattr(self, 'can_view_transfer_details', False),
            'edit_transfers_data': getattr(self, 'can_edit_transfers_data', False),
            'add_new_transfer': getattr(self, 'can_add_new_transfer', False),
            'delete_transfer': getattr(self, 'can_delete_transfer', False),
            
            # Report permissions
            'view_employee_reports': getattr(self, 'can_view_employee_reports', False),
            'view_school_reports': getattr(self, 'can_view_school_reports', False),
            'view_comprehensive_reports': getattr(self, 'can_view_comprehensive_reports', False),
            
            # Export permissions
            'export_employee_data': getattr(self, 'can_export_employee_data', False),
            'export_school_data': getattr(self, 'can_export_school_data', False),
            'export_report_data': getattr(self, 'can_export_report_data', False),
            
            # User management permissions
            'view_users_list': getattr(self, 'can_view_users_list', False),
            'add_new_user': getattr(self, 'can_add_new_user', False),
            'manage_user_permissions': getattr(self, 'can_manage_user_permissions', False),
            
            # Form permissions
            'view_forms_list': getattr(self, 'can_view_forms_list', False),
            'edit_forms_data': getattr(self, 'can_edit_forms_data', False),
            'add_new_form': getattr(self, 'can_add_new_form', False),
            'delete_form': getattr(self, 'can_delete_form', False),
            
            # System permissions
            'view_system_logs': getattr(self, 'can_view_system_logs', False),
            'backup_database': getattr(self, 'can_backup_database', False),
            'manage_system_settings': getattr(self, 'can_manage_system_settings', False),
            'process_monthly_departures': getattr(self, 'can_process_monthly_departures', False),
            
            # الصلاحيات المستخدمة في القوالب (base.html)
            'can_view_employees': getattr(self, 'can_view_employees_list', False) or getattr(self, 'can_view_employees', False),
            'can_manage_employees': getattr(self, 'can_edit_employees_data', False) or getattr(self, 'can_add_new_employee', False) or getattr(self, 'can_delete_employee', False),
            'can_manage_schools': getattr(self, 'can_edit_schools_data', False) or getattr(self, 'can_add_new_school', False) or getattr(self, 'can_delete_school', False),
            'can_manage_transfers': getattr(self, 'can_edit_transfers_data', False) or getattr(self, 'can_add_new_transfer', False) or getattr(self, 'can_delete_transfer', False),
            'can_view_leaves': getattr(self, 'can_view_leaves_list', False) or getattr(self, 'can_view_leaves', False),
            'can_manage_leaves': getattr(self, 'can_edit_leaves_data', False) or getattr(self, 'can_add_new_leave', False) or getattr(self, 'can_delete_leave', False),
            'can_view_departures': getattr(self, 'can_view_departures_list', False) or getattr(self, 'can_view_departures', False),
            'can_manage_departures': getattr(self, 'can_edit_departures_data', False) or getattr(self, 'can_add_new_departure', False) or getattr(self, 'can_delete_departure', False),
            'can_manage_leave_balances': getattr(self, 'can_manage_leave_balances', False),
            'can_view_reports': getattr(self, 'can_view_employee_reports', False) or getattr(self, 'can_view_school_reports', False) or getattr(self, 'can_view_comprehensive_reports', False),
            'can_view_employee_reports': getattr(self, 'can_view_employee_reports', False),
            'can_view_school_reports': getattr(self, 'can_view_school_reports', False),
            'can_view_leave_reports': getattr(self, 'can_view_leave_reports', False),
            'can_view_departure_reports': getattr(self, 'can_view_departure_reports', False),
            'can_view_comprehensive_reports': getattr(self, 'can_view_comprehensive_reports', False),
            'can_manage_forms': getattr(self, 'can_edit_forms_data', False) or getattr(self, 'can_add_new_form', False) or getattr(self, 'can_delete_form', False),
            
            # صلاحيات إضافية للتوافق
            'view_users': getattr(self, 'can_view_users_list', False),
            'edit_users': getattr(self, 'can_manage_user_permissions', False),
            'view_employees': getattr(self, 'can_view_employees_list', False) or getattr(self, 'can_view_employees', False),
            'edit_employees': getattr(self, 'can_edit_employees_data', False) or getattr(self, 'can_edit_employees', False),
        }
        
        if permission:
            return permission_map.get(permission, False)
        else:
            return permission_map

'''
        
        # دمج المحتوى الجديد
        new_content = before_function + new_function + after_function
        
        # كتابة الملف الجديد
        with open(models_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ تم إصلاح دالة has_permission بنجاح!")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في إصلاح الدالة: {e}")
        return False

def fix_database_permissions():
    """
    إصلاح قاعدة البيانات والصلاحيات
    """
    
    # مسار قاعدة البيانات
    db_path = os.path.join('instance', 'employees.db')
    
    if not os.path.exists(db_path):
        print("❌ خطأ: لم يتم العثور على قاعدة البيانات")
        return False
    
    try:
        # الاتصال بقاعدة البيانات
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 فحص قاعدة البيانات...")
        
        # فحص جدول المستخدمين
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")
        if not cursor.fetchone():
            print("❌ جدول المستخدمين غير موجود!")
            return False
        
        # قائمة الصلاحيات المطلوبة
        required_permissions = [
            'is_admin', 'can_backup_database',
            'can_view_employees_list', 'can_view_employee_details', 'can_edit_employees_data', 'can_add_new_employee', 'can_delete_employee',
            'can_view_schools_list', 'can_view_school_details', 'can_edit_schools_data', 'can_add_new_school', 'can_delete_school',
            'can_view_leaves_list', 'can_view_leave_details', 'can_edit_leaves_data', 'can_add_new_leave', 'can_delete_leave', 'can_manage_leave_balances',
            'can_view_departures_list', 'can_view_departure_details', 'can_edit_departures_data', 'can_add_new_departure', 'can_delete_departure',
            'can_view_transfers_list', 'can_view_transfer_details', 'can_edit_transfers_data', 'can_add_new_transfer', 'can_delete_transfer',
            'can_view_employee_reports', 'can_view_school_reports', 'can_view_comprehensive_reports',
            'can_export_employee_data', 'can_export_school_data', 'can_export_report_data',
            'can_view_users_list', 'can_add_new_user', 'can_manage_user_permissions',
            'can_view_forms_list', 'can_edit_forms_data', 'can_add_new_form', 'can_delete_form',
            'can_view_system_logs', 'can_manage_system_settings', 'can_process_monthly_departures',
            'can_view_employees', 'can_add_employees', 'can_edit_employees', 'can_delete_employees',
            'can_view_leaves', 'can_add_leaves', 'can_edit_leaves', 'can_delete_leaves', 'can_approve_leaves',
            'can_view_departures', 'can_add_departures', 'can_edit_departures', 'can_delete_departures', 'can_convert_departures',
            'can_view_leave_reports', 'can_view_departure_reports',
            'can_export_employees', 'can_export_leaves', 'can_export_departures', 'can_export_balances', 'can_export_reports',
            'can_view_statistics', 'can_view_own_school_only', 'can_manage_school_employees', 'can_view_school_statistics'
        ]
        
        # فحص الأعمدة الموجودة
        cursor.execute("PRAGMA table_info(user)")
        columns = cursor.fetchall()
        existing_columns = [col[1] for col in columns]
        
        # إضافة الأعمدة المفقودة
        missing_permissions = [perm for perm in required_permissions if perm not in existing_columns]
        
        if missing_permissions:
            print(f"⚠️  إضافة {len(missing_permissions)} عمود صلاحيات مفقود...")
            for perm in missing_permissions:
                try:
                    cursor.execute(f"ALTER TABLE user ADD COLUMN {perm} BOOLEAN DEFAULT 0")
                    print(f"   ✅ تم إضافة: {perm}")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" not in str(e):
                        print(f"   ❌ خطأ في إضافة {perm}: {e}")
        
        # الحصول على قائمة محدثة بالأعمدة
        cursor.execute("PRAGMA table_info(user)")
        columns = cursor.fetchall()
        current_permission_columns = [col[1] for col in columns if col[1].startswith('can_') or col[1] == 'is_admin']
        
        # إنشاء/تحديث المستخدمين الأساسيين
        users_to_create = [
            ('admin', 'admin123', 'مدير النظام'),
            ('wael', '123456', 'وائل')
        ]
        
        for username, password, full_name in users_to_create:
            # التحقق من وجود المستخدم
            cursor.execute("SELECT id FROM user WHERE username = ?", (username,))
            user = cursor.fetchone()
            
            if not user:
                # إنشاء المستخدم
                password_hash = generate_password_hash(password)
                cursor.execute(
                    "INSERT INTO user (username, password_hash, full_name, is_admin) VALUES (?, ?, ?, ?)",
                    (username, password_hash, full_name, 1)
                )
                print(f"✅ تم إنشاء المستخدم: {username}")
                user_id = cursor.lastrowid
            else:
                user_id = user[0]
                # تحديث كلمة المرور والحالة الإدارية
                password_hash = generate_password_hash(password)
                cursor.execute(
                    "UPDATE user SET password_hash = ?, is_admin = 1 WHERE id = ?",
                    (password_hash, user_id)
                )
                print(f"✅ تم تحديث المستخدم: {username}")
            
            # منح جميع الصلاحيات
            update_parts = []
            for perm in current_permission_columns:
                if perm != 'is_admin':
                    update_parts.append(f"{perm} = 1")
            
            if update_parts:
                update_query = f"UPDATE user SET {', '.join(update_parts)} WHERE id = ?"
                cursor.execute(update_query, (user_id,))
                print(f"   ✅ تم منح جميع الصلاحيات ({len(update_parts)} صلاحية)")
        
        # حفظ التغييرات
        conn.commit()
        
        print("✅ تم إصلاح قاعدة البيانات والصلاحيات بنجاح!")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في إصلاح قاعدة البيانات: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    try:
        success = complete_system_fix()
        
        if success:
            print("\n" + "=" * 60)
            print("🎉 تم إصلاح جميع مشاكل النظام بنجاح!")
            print("\n📋 ملخص الإصلاحات:")
            print("   ✅ تم إصلاح دالة has_permission")
            print("   ✅ تم إصلاح قاعدة البيانات والصلاحيات")
            print("   ✅ تم إنشاء/تحديث المستخدمين الأساسيين")
            print("   ✅ تم منح جميع الصلاحيات للمديرين")
            
            print("\n🔐 بيانات تسجيل الدخول:")
            print("   المدير: admin / admin123")
            print("   وائل: wael / 123456")
            
            print("\n⚠️  تعليمات مهمة:")
            print("   1. أعد تشغيل التطبيق الآن")
            print("   2. سجل دخول بأي من الحسابين أعلاه")
            print("   3. يجب أن تظهر جميع القوائم والصلاحيات الآن")
        else:
            print("\n❌ فشل في إصلاح النظام")
            
    except Exception as e:
        print(f"❌ خطأ عام: {e}")
    
    input("\nاضغط Enter للخروج...")