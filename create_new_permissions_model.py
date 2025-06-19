from app import app, db
from models import User
from sqlalchemy import text

def create_new_permissions_structure():
    """إنشاء هيكل جديد للصلاحيات مع فصل المشاهدة والتعديل"""
    
    with app.app_context():
        # إضافة الأعمدة الجديدة للصلاحيات المنظمة
        new_permissions = [
            # صلاحيات الموظفين
            'can_view_employees_list',
            'can_edit_employees_data',
            'can_view_employee_details',
            'can_edit_employee_details',
            'can_add_new_employee',
            'can_delete_employee',
            
            # صلاحيات المدارس
            'can_view_schools_list',
            'can_edit_schools_data',
            'can_view_school_details',
            'can_edit_school_details',
            'can_add_new_school',
            'can_delete_school',
            
            # صلاحيات الإجازات
            'can_view_leaves_list',
            'can_edit_leaves_data',
            'can_view_leave_details',
            'can_edit_leave_details',
            'can_add_new_leave',
            'can_delete_leave',
            'can_approve_leave_requests',
            'can_manage_leave_balances',
            
            # صلاحيات المغادرات
            'can_view_departures_list',
            'can_edit_departures_data',
            'can_view_departure_details',
            'can_edit_departure_details',
            'can_add_new_departure',
            'can_delete_departure',
            'can_convert_departures_to_leaves',
            'can_process_monthly_departures',
            
            # صلاحيات النقل
            'can_view_transfers_list',
            'can_edit_transfers_data',
            'can_view_transfer_details',
            'can_edit_transfer_details',
            'can_add_new_transfer',
            'can_delete_transfer',
            
            # صلاحيات التقارير
            'can_view_employee_reports',
            'can_view_school_reports',
            'can_view_leave_reports',
            'can_view_departure_reports',
            'can_view_transfer_reports',
            'can_view_comprehensive_reports',
            'can_view_statistical_reports',
            
            # صلاحيات التصدير
            'can_export_employee_data',
            'can_export_school_data',
            'can_export_leave_data',
            'can_export_departure_data',
            'can_export_transfer_data',
            'can_export_report_data',
            'can_export_balance_data',
            
            # صلاحيات إدارة المستخدمين
            'can_view_users_list',
            'can_edit_users_data',
            'can_view_user_details',
            'can_edit_user_details',
            'can_add_new_user',
            'can_delete_user',
            'can_manage_user_permissions',
            
            # صلاحيات النماذج
            'can_view_forms_list',
            'can_edit_forms_data',
            'can_add_new_form',
            'can_delete_form',
            
            # صلاحيات النظام
            'can_view_system_logs',
            'can_view_system_statistics',
            'can_manage_system_settings',
            'can_backup_database',
            'can_restore_database',
            
            # صلاحيات خاصة
            'can_view_own_school_data_only',
            'can_manage_own_school_employees',
            'can_view_directorate_data',
            'can_manage_directorate_employees'
        ]
        
        try:
            # إضافة الأعمدة الجديدة
            for permission in new_permissions:
                try:
                    db.engine.execute(text(f'ALTER TABLE user ADD COLUMN {permission} BOOLEAN DEFAULT FALSE'))
                    print(f"تم إضافة العمود: {permission}")
                except Exception as e:
                    if "duplicate column name" in str(e).lower():
                        print(f"العمود {permission} موجود بالفعل")
                    else:
                        print(f"خطأ في إضافة العمود {permission}: {e}")
            
            db.session.commit()
            print("تم إنشاء هيكل الصلاحيات الجديد بنجاح!")
            
        except Exception as e:
            print(f"خطأ في إنشاء هيكل الصلاحيات: {e}")
            db.session.rollback()

if __name__ == '__main__':
    create_new_permissions_structure()