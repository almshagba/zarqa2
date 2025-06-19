#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إصلاح شامل لنظام الصلاحيات
يحل جميع المشاكل الموجودة في نظام الصلاحيات ويعيد تنظيمه
"""

import os
import sys
import shutil
from datetime import datetime
import sqlite3

def backup_files():
    """إنشاء نسخ احتياطية من الملفات المهمة"""
    print("📁 إنشاء نسخ احتياطية...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    files_to_backup = [
        'models.py',
        'routes/auth_routes.py',
        'new_user_routes.py',
        'templates/base.html'
    ]
    
    for file_path in files_to_backup:
        if os.path.exists(file_path):
            backup_path = f"{file_path}_backup_{timestamp}"
            shutil.copy2(file_path, backup_path)
            print(f"✅ تم إنشاء نسخة احتياطية: {backup_path}")
        else:
            print(f"⚠️ الملف غير موجود: {file_path}")

def fix_models_has_permission():
    """إصلاح دالة has_permission في models.py"""
    print("🔧 إصلاح دالة has_permission في models.py...")
    
    models_file = 'models.py'
    
    if not os.path.exists(models_file):
        print("❌ خطأ: ملف models.py غير موجود")
        return False
    
    # قراءة الملف الحالي
    with open(models_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # البحث عن بداية ونهاية دالة has_permission
    start_marker = "def has_permission(self, permission=None):"
    end_marker = "def __repr__(self):"
    
    start_index = content.find(start_marker)
    end_index = content.find(end_marker)
    
    if start_index == -1 or end_index == -1:
        print("❌ لم يتم العثور على دالة has_permission")
        return False
    
    # الدالة الجديدة المحسنة
    new_function = '''    def has_permission(self, permission=None):
        """فحص الصلاحيات - يدعم فحص صلاحية واحدة أو إرجاع جميع الصلاحيات"""
        if self.is_admin:
            # المدير لديه جميع الصلاحيات
            if permission:
                return True
            else:
                # إرجاع قاموس بجميع الصلاحيات للمدير
                all_permissions = {}
                # جميع الصلاحيات الأساسية
                basic_perms = [
                    # صلاحيات الموظفين
                    'view_employees_list', 'view_employee_details', 'edit_employees_data', 
                    'add_new_employee', 'delete_employee', 'can_view_employees', 'can_manage_employees',
                    'view_employees', 'edit_employees', 'can_add_employees', 'can_edit_employees', 'can_delete_employees',
                    
                    # صلاحيات المدارس
                    'view_schools_list', 'view_school_details', 'edit_schools_data', 
                    'add_new_school', 'delete_school', 'can_manage_schools',
                    
                    # صلاحيات الإجازات
                    'view_leaves_list', 'view_leave_details', 'edit_leaves_data', 
                    'add_new_leave', 'delete_leave', 'manage_leave_balances', 'can_view_leaves', 
                    'can_manage_leaves', 'can_add_leaves', 'can_edit_leaves', 'can_delete_leaves',
                    'can_approve_leaves', 'can_manage_leave_balances',
                    
                    # صلاحيات المغادرات
                    'view_departures_list', 'view_departure_details', 'edit_departures_data',
                    'add_new_departure', 'delete_departure', 'can_view_departures', 'can_manage_departures',
                    'can_add_departures', 'can_edit_departures', 'can_delete_departures', 'can_convert_departures',
                    
                    # صلاحيات النقل
                    'view_transfers_list', 'view_transfer_details', 'edit_transfers_data',
                    'add_new_transfer', 'delete_transfer', 'can_manage_transfers',
                    
                    # صلاحيات التقارير
                    'view_employee_reports', 'view_school_reports', 'view_comprehensive_reports',
                    'can_view_reports', 'can_view_employee_reports', 'can_view_school_reports',
                    'can_view_leave_reports', 'can_view_departure_reports', 'can_view_comprehensive_reports',
                    
                    # صلاحيات التصدير
                    'export_employee_data', 'export_school_data', 'export_report_data',
                    'can_export_data', 'can_export_employees', 'can_export_leaves', 
                    'can_export_departures', 'can_export_balances', 'can_export_reports',
                    
                    # صلاحيات إدارة المستخدمين
                    'view_users_list', 'add_new_user', 'manage_user_permissions',
                    'can_manage_users', 'view_users', 'edit_users',
                    
                    # صلاحيات النماذج
                    'view_forms_list', 'edit_forms_data', 'add_new_form', 'delete_form', 'can_manage_forms',
                    
                    # صلاحيات النظام
                    'view_system_logs', 'backup_database', 'manage_system_settings', 
                    'process_monthly_departures', 'can_backup_database', 'can_view_system_logs',
                    'can_manage_system_settings', 'can_process_monthly_departures', 'can_view_statistics',
                    
                    # صلاحيات خاصة
                    'can_view_own_school_only', 'can_manage_school_employees', 'can_view_school_statistics'
                ]
                for perm in basic_perms:
                    all_permissions[perm] = True
                return all_permissions
        
        # للمستخدمين العاديين - إنشاء خريطة الصلاحيات
        permission_map = {
            # صلاحيات الموظفين
            'view_employees_list': getattr(self, 'can_view_employees_list', False),
            'view_employee_details': getattr(self, 'can_view_employee_details', False),
            'edit_employees_data': getattr(self, 'can_edit_employees_data', False),
            'add_new_employee': getattr(self, 'can_add_new_employee', False),
            'delete_employee': getattr(self, 'can_delete_employee', False),
            'can_view_employees': getattr(self, 'can_view_employees_list', False) or getattr(self, 'can_view_employees', False),
            'can_manage_employees': (getattr(self, 'can_edit_employees_data', False) or 
                                   getattr(self, 'can_add_new_employee', False) or 
                                   getattr(self, 'can_delete_employee', False) or
                                   getattr(self, 'can_edit_employees', False) or
                                   getattr(self, 'can_add_employees', False) or
                                   getattr(self, 'can_delete_employees', False)),
            'view_employees': getattr(self, 'can_view_employees_list', False) or getattr(self, 'can_view_employees', False),
            'edit_employees': getattr(self, 'can_edit_employees_data', False) or getattr(self, 'can_edit_employees', False),
            'can_add_employees': getattr(self, 'can_add_new_employee', False) or getattr(self, 'can_add_employees', False),
            'can_edit_employees': getattr(self, 'can_edit_employees_data', False) or getattr(self, 'can_edit_employees', False),
            'can_delete_employees': getattr(self, 'can_delete_employee', False) or getattr(self, 'can_delete_employees', False),
            
            # صلاحيات المدارس
            'view_schools_list': getattr(self, 'can_view_schools_list', False),
            'view_school_details': getattr(self, 'can_view_school_details', False),
            'edit_schools_data': getattr(self, 'can_edit_schools_data', False),
            'add_new_school': getattr(self, 'can_add_new_school', False),
            'delete_school': getattr(self, 'can_delete_school', False),
            'can_manage_schools': (getattr(self, 'can_edit_schools_data', False) or 
                                 getattr(self, 'can_add_new_school', False) or 
                                 getattr(self, 'can_delete_school', False)),
            
            # صلاحيات الإجازات
            'view_leaves_list': getattr(self, 'can_view_leaves_list', False),
            'view_leave_details': getattr(self, 'can_view_leave_details', False),
            'edit_leaves_data': getattr(self, 'can_edit_leaves_data', False),
            'add_new_leave': getattr(self, 'can_add_new_leave', False),
            'delete_leave': getattr(self, 'can_delete_leave', False),
            'manage_leave_balances': getattr(self, 'can_manage_leave_balances', False),
            'can_view_leaves': getattr(self, 'can_view_leaves_list', False) or getattr(self, 'can_view_leaves', False),
            'can_manage_leaves': (getattr(self, 'can_edit_leaves_data', False) or 
                                getattr(self, 'can_add_new_leave', False) or 
                                getattr(self, 'can_delete_leave', False) or
                                getattr(self, 'can_edit_leaves', False) or
                                getattr(self, 'can_add_leaves', False) or
                                getattr(self, 'can_delete_leaves', False)),
            'can_add_leaves': getattr(self, 'can_add_new_leave', False) or getattr(self, 'can_add_leaves', False),
            'can_edit_leaves': getattr(self, 'can_edit_leaves_data', False) or getattr(self, 'can_edit_leaves', False),
            'can_delete_leaves': getattr(self, 'can_delete_leave', False) or getattr(self, 'can_delete_leaves', False),
            'can_approve_leaves': getattr(self, 'can_approve_leaves', False),
            'can_manage_leave_balances': getattr(self, 'can_manage_leave_balances', False),
            
            # صلاحيات المغادرات
            'view_departures_list': getattr(self, 'can_view_departures_list', False),
            'view_departure_details': getattr(self, 'can_view_departure_details', False),
            'edit_departures_data': getattr(self, 'can_edit_departures_data', False),
            'add_new_departure': getattr(self, 'can_add_new_departure', False),
            'delete_departure': getattr(self, 'can_delete_departure', False),
            'can_view_departures': getattr(self, 'can_view_departures_list', False) or getattr(self, 'can_view_departures', False),
            'can_manage_departures': (getattr(self, 'can_edit_departures_data', False) or 
                                    getattr(self, 'can_add_new_departure', False) or 
                                    getattr(self, 'can_delete_departure', False) or
                                    getattr(self, 'can_edit_departures', False) or
                                    getattr(self, 'can_add_departures', False) or
                                    getattr(self, 'can_delete_departures', False)),
            'can_add_departures': getattr(self, 'can_add_new_departure', False) or getattr(self, 'can_add_departures', False),
            'can_edit_departures': getattr(self, 'can_edit_departures_data', False) or getattr(self, 'can_edit_departures', False),
            'can_delete_departures': getattr(self, 'can_delete_departure', False) or getattr(self, 'can_delete_departures', False),
            'can_convert_departures': getattr(self, 'can_convert_departures', False),
            
            # صلاحيات النقل
            'view_transfers_list': getattr(self, 'can_view_transfers_list', False),
            'view_transfer_details': getattr(self, 'can_view_transfer_details', False),
            'edit_transfers_data': getattr(self, 'can_edit_transfers_data', False),
            'add_new_transfer': getattr(self, 'can_add_new_transfer', False),
            'delete_transfer': getattr(self, 'can_delete_transfer', False),
            'can_manage_transfers': (getattr(self, 'can_edit_transfers_data', False) or 
                                   getattr(self, 'can_add_new_transfer', False) or 
                                   getattr(self, 'can_delete_transfer', False)),
            
            # صلاحيات التقارير
            'view_employee_reports': getattr(self, 'can_view_employee_reports', False),
            'view_school_reports': getattr(self, 'can_view_school_reports', False),
            'view_comprehensive_reports': getattr(self, 'can_view_comprehensive_reports', False),
            'can_view_reports': (getattr(self, 'can_view_employee_reports', False) or 
                               getattr(self, 'can_view_school_reports', False) or 
                               getattr(self, 'can_view_comprehensive_reports', False)),
            'can_view_employee_reports': getattr(self, 'can_view_employee_reports', False),
            'can_view_school_reports': getattr(self, 'can_view_school_reports', False),
            'can_view_leave_reports': getattr(self, 'can_view_leave_reports', False),
            'can_view_departure_reports': getattr(self, 'can_view_departure_reports', False),
            'can_view_comprehensive_reports': getattr(self, 'can_view_comprehensive_reports', False),
            
            # صلاحيات التصدير
            'export_employee_data': getattr(self, 'can_export_employee_data', False),
            'export_school_data': getattr(self, 'can_export_school_data', False),
            'export_report_data': getattr(self, 'can_export_report_data', False),
            'can_export_data': (getattr(self, 'can_export_employee_data', False) or 
                              getattr(self, 'can_export_school_data', False) or 
                              getattr(self, 'can_export_report_data', False)),
            'can_export_employees': getattr(self, 'can_export_employee_data', False) or getattr(self, 'can_export_employees', False),
            'can_export_leaves': getattr(self, 'can_export_leaves', False),
            'can_export_departures': getattr(self, 'can_export_departures', False),
            'can_export_balances': getattr(self, 'can_export_balances', False),
            'can_export_reports': getattr(self, 'can_export_report_data', False) or getattr(self, 'can_export_reports', False),
            
            # صلاحيات إدارة المستخدمين
            'view_users_list': getattr(self, 'can_view_users_list', False),
            'add_new_user': getattr(self, 'can_add_new_user', False),
            'manage_user_permissions': getattr(self, 'can_manage_user_permissions', False),
            'can_manage_users': (getattr(self, 'can_view_users_list', False) or 
                               getattr(self, 'can_add_new_user', False) or 
                               getattr(self, 'can_manage_user_permissions', False)),
            'view_users': getattr(self, 'can_view_users_list', False),
            'edit_users': getattr(self, 'can_manage_user_permissions', False),
            
            # صلاحيات النماذج
            'view_forms_list': getattr(self, 'can_view_forms_list', False),
            'edit_forms_data': getattr(self, 'can_edit_forms_data', False),
            'add_new_form': getattr(self, 'can_add_new_form', False),
            'delete_form': getattr(self, 'can_delete_form', False),
            'can_manage_forms': (getattr(self, 'can_edit_forms_data', False) or 
                               getattr(self, 'can_add_new_form', False) or 
                               getattr(self, 'can_delete_form', False)),
            
            # صلاحيات النظام
            'view_system_logs': getattr(self, 'can_view_system_logs', False),
            'backup_database': getattr(self, 'can_backup_database', False),
            'manage_system_settings': getattr(self, 'can_manage_system_settings', False),
            'process_monthly_departures': getattr(self, 'can_process_monthly_departures', False),
            'can_backup_database': getattr(self, 'can_backup_database', False),
            'can_view_system_logs': getattr(self, 'can_view_system_logs', False),
            'can_manage_system_settings': getattr(self, 'can_manage_system_settings', False),
            'can_process_monthly_departures': getattr(self, 'can_process_monthly_departures', False),
            'can_view_statistics': getattr(self, 'can_view_statistics', False),
            
            # صلاحيات خاصة
            'can_view_own_school_only': getattr(self, 'can_view_own_school_only', False),
            'can_manage_school_employees': getattr(self, 'can_manage_school_employees', False),
            'can_view_school_statistics': getattr(self, 'can_view_school_statistics', False)
        }
        
        if permission:
            return permission_map.get(permission, False)
        else:
            return permission_map

    '''
    
    # استبدال الدالة القديمة بالجديدة
    new_content = content[:start_index] + new_function + content[end_index:]
    
    # كتابة الملف المحدث
    with open(models_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ تم إصلاح دالة has_permission في models.py")
    return True

def fix_auth_routes():
    """إصلاح دالة permission_required في auth_routes.py"""
    print("🔧 إصلاح دالة permission_required في auth_routes.py...")
    
    auth_file = 'routes/auth_routes.py'
    
    if not os.path.exists(auth_file):
        print("❌ خطأ: ملف auth_routes.py غير موجود")
        return False
    
    # قراءة الملف الحالي
    with open(auth_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # البحث عن دالة permission_required واستبدالها
    old_function = '''def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('يرجى تسجيل الدخول أولاً', 'danger')
                return redirect(url_for('auth.login'))
            
            user = User.query.get(session['user_id'])
            if not user or not user.has_permission(permission):
                flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
                return redirect(url_for('main.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator'''
    
    new_function = '''def permission_required(permission):
    """ديكوريتر للتحقق من الصلاحيات"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # التحقق من تسجيل الدخول
            if 'user_id' not in session:
                flash('يرجى تسجيل الدخول أولاً', 'danger')
                return redirect(url_for('auth.login'))
            
            # الحصول على المستخدم
            user = User.query.get(session['user_id'])
            if not user:
                flash('المستخدم غير موجود', 'danger')
                return redirect(url_for('auth.login'))
            
            # التحقق من الصلاحية
            try:
                has_perm = user.has_permission(permission)
                if not has_perm:
                    flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
                    return redirect(url_for('main.index'))
            except Exception as e:
                print(f"خطأ في فحص الصلاحية {permission}: {e}")
                flash('خطأ في فحص الصلاحيات', 'danger')
                return redirect(url_for('main.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator'''
    
    # استبدال الدالة
    if old_function in content:
        content = content.replace(old_function, new_function)
        
        # كتابة الملف المحدث
        with open(auth_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ تم إصلاح دالة permission_required في auth_routes.py")
        return True
    else:
        print("⚠️ لم يتم العثور على الدالة القديمة في auth_routes.py")
        return False

def fix_new_user_routes():
    """إصلاح دالة check_permission في new_user_routes.py"""
    print("🔧 إصلاح دالة check_permission في new_user_routes.py...")
    
    new_user_file = 'new_user_routes.py'
    
    if not os.path.exists(new_user_file):
        print("❌ خطأ: ملف new_user_routes.py غير موجود")
        return False
    
    # قراءة الملف الحالي
    with open(new_user_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # البحث عن دالة check_permission واستبدالها
    old_function = '''def check_permission(permission_name):
    """فحص صلاحية المستخدم"""
    if current_user.is_admin:
        return True
    return current_user.has_permission().get(permission_name, False)'''
    
    new_function = '''def check_permission(permission_name):
    """فحص صلاحية المستخدم بطريقة محسنة"""
    try:
        if not current_user.is_authenticated:
            return False
        
        if current_user.is_admin:
            return True
        
        # الحصول على الصلاحيات
        permissions = current_user.has_permission()
        if isinstance(permissions, dict):
            return permissions.get(permission_name, False)
        else:
            # في حالة تم تمرير صلاحية واحدة
            return current_user.has_permission(permission_name)
    except Exception as e:
        print(f"خطأ في فحص الصلاحية {permission_name}: {e}")
        return False'''
    
    # استبدال الدالة
    if old_function in content:
        content = content.replace(old_function, new_function)
        
        # كتابة الملف المحدث
        with open(new_user_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ تم إصلاح دالة check_permission في new_user_routes.py")
        return True
    else:
        print("⚠️ لم يتم العثور على الدالة القديمة في new_user_routes.py")
        return False

def create_permission_test_script():
    """إنشاء سكريبت لاختبار الصلاحيات"""
    print("📝 إنشاء سكريبت اختبار الصلاحيات...")
    
    test_script = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت اختبار نظام الصلاحيات
"""

from app import app
from models import User, db

def test_permissions():
    """اختبار نظام الصلاحيات"""
    with app.app_context():
        print("🧪 اختبار نظام الصلاحيات...")
        
        # البحث عن مستخدم مدير
        admin_user = User.query.filter_by(is_admin=True).first()
        if admin_user:
            print(f"✅ تم العثور على مستخدم مدير: {admin_user.username}")
            
            # اختبار صلاحيات المدير
            perms = admin_user.has_permission()
            print(f"📊 عدد صلاحيات المدير: {len(perms)}")
            
            # اختبار صلاحية واحدة
            test_perm = admin_user.has_permission('can_view_employees')
            print(f"🔍 صلاحية can_view_employees للمدير: {test_perm}")
        else:
            print("❌ لم يتم العثور على مستخدم مدير")
        
        # البحث عن مستخدم عادي
        normal_user = User.query.filter_by(is_admin=False).first()
        if normal_user:
            print(f"✅ تم العثور على مستخدم عادي: {normal_user.username}")
            
            # اختبار صلاحيات المستخدم العادي
            perms = normal_user.has_permission()
            active_perms = [k for k, v in perms.items() if v]
            print(f"📊 عدد الصلاحيات النشطة للمستخدم العادي: {len(active_perms)}")
            print(f"📋 الصلاحيات النشطة: {active_perms[:5]}...")  # أول 5 صلاحيات
        else:
            print("❌ لم يتم العثور على مستخدم عادي")
        
        print("✅ انتهى اختبار نظام الصلاحيات")

if __name__ == '__main__':
    test_permissions()
'''
    
    with open('test_permissions.py', 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print("✅ تم إنشاء سكريبت اختبار الصلاحيات: test_permissions.py")

def main():
    """الدالة الرئيسية"""
    print("🚀 بدء إصلاح نظام الصلاحيات...")
    print("=" * 50)
    
    try:
        # إنشاء نسخ احتياطية
        backup_files()
        print()
        
        # إصلاح دالة has_permission في models.py
        if fix_models_has_permission():
            print("✅ تم إصلاح models.py بنجاح")
        else:
            print("❌ فشل في إصلاح models.py")
        print()
        
        # إصلاح دالة permission_required في auth_routes.py
        if fix_auth_routes():
            print("✅ تم إصلاح auth_routes.py بنجاح")
        else:
            print("❌ فشل في إصلاح auth_routes.py")
        print()
        
        # إصلاح دالة check_permission في new_user_routes.py
        if fix_new_user_routes():
            print("✅ تم إصلاح new_user_routes.py بنجاح")
        else:
            print("❌ فشل في إصلاح new_user_routes.py")
        print()
        
        # إنشاء سكريبت اختبار
        create_permission_test_script()
        print()
        
        print("🎉 تم إصلاح نظام الصلاحيات بنجاح!")
        print("=" * 50)
        print("📋 الخطوات التالية:")
        print("1. أعد تشغيل الخادم: python app.py")
        print("2. اختبر النظام: python test_permissions.py")
        print("3. تحقق من عمل الصلاحيات في الواجهة")
        
    except Exception as e:
        print(f"❌ خطأ في إصلاح النظام: {e}")
        return False
    
    return True

if __name__ == '__main__':
    main()