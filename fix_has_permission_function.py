#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إصلاح دالة has_permission في ملف models.py
"""

import os
import shutil
from datetime import datetime

def fix_has_permission_function():
    """
    إصلاح دالة has_permission لتعمل مع جميع الصلاحيات بشكل صحيح
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
        end_marker = "return permission_map.get(permission, False)"
        
        start_index = content.find(start_marker)
        if start_index == -1:
            print("❌ لم يتم العثور على دالة has_permission")
            return False
        
        end_index = content.find(end_marker, start_index)
        if end_index == -1:
            print("❌ لم يتم العثور على نهاية دالة has_permission")
            return False
        
        # إزالة الدالة القديمة
        end_index = content.find('\n', end_index) + 1
        before_function = content[:start_index]
        after_function = content[end_index:]
        
        # الدالة الجديدة المحسنة
        new_function = '''def has_permission(self, permission=None):
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
        print("\n📋 التحسينات المطبقة:")
        print("   - دعم كامل للمديرين (جميع الصلاحيات)")
        print("   - دعم الصلاحيات المستخدمة في القوالب")
        print("   - استخدام getattr لتجنب أخطاء الأعمدة المفقودة")
        print("   - دعم استدعاء الدالة بمعامل أو بدون معامل")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في إصلاح الدالة: {e}")
        return False

if __name__ == "__main__":
    try:
        print("🔧 بدء إصلاح دالة has_permission")
        print("=" * 40)
        
        success = fix_has_permission_function()
        
        if success:
            print("\n🎉 تم إصلاح دالة has_permission بنجاح!")
            print("\n⚠️  تعليمات مهمة:")
            print("   1. أعد تشغيل التطبيق")
            print("   2. شغل comprehensive_check.bat لإصلاح الصلاحيات")
            print("   3. سجل دخول بحساب المدير أو وائل")
        else:
            print("\n❌ فشل في إصلاح الدالة")
            
    except Exception as e:
        print(f"❌ خطأ عام: {e}")
    
    input("\nاضغط Enter للخروج...")