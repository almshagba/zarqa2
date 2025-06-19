import sqlite3
import os
from datetime import datetime

def fix_database_schema():
    db_path = 'instance/employees.db'
    
    if not os.path.exists(db_path):
        print("قاعدة البيانات غير موجودة")
        return
    
    try:
        # الاتصال بقاعدة البيانات
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # فحص الأعمدة الموجودة في جدول user
        cursor.execute("PRAGMA table_info(user)")
        columns = cursor.fetchall()
        
        print("الأعمدة الموجودة في جدول user:")
        for col in columns:
            print(f"- {col[1]} ({col[2]})")
        
        # إنشاء جدول جديد بالبنية الصحيحة
        cursor.execute("""
        CREATE TABLE user_new (
            id INTEGER PRIMARY KEY,
            username VARCHAR(64) UNIQUE NOT NULL,
            password_hash VARCHAR(128) NOT NULL,
            full_name VARCHAR(100) NOT NULL,
            is_admin BOOLEAN DEFAULT 0,
            created_at DATETIME,
            can_backup_database BOOLEAN DEFAULT 0,
            
            -- Employee permissions
            can_view_employees_list BOOLEAN DEFAULT 0,
            can_view_employee_details BOOLEAN DEFAULT 0,
            can_edit_employees_data BOOLEAN DEFAULT 0,
            can_add_new_employee BOOLEAN DEFAULT 0,
            can_delete_employee BOOLEAN DEFAULT 0,
            
            -- School permissions  
            can_view_schools_list BOOLEAN DEFAULT 0,
            can_view_school_details BOOLEAN DEFAULT 0,
            can_edit_schools_data BOOLEAN DEFAULT 0,
            can_add_new_school BOOLEAN DEFAULT 0,
            can_delete_school BOOLEAN DEFAULT 0,
            
            -- Leave permissions
            can_view_leaves_list BOOLEAN DEFAULT 0,
            can_view_leave_details BOOLEAN DEFAULT 0,
            can_edit_leaves_data BOOLEAN DEFAULT 0,
            can_add_new_leave BOOLEAN DEFAULT 0,
            can_delete_leave BOOLEAN DEFAULT 0,
            can_manage_leave_balances BOOLEAN DEFAULT 0,
            can_delete_leaves BOOLEAN DEFAULT 0,
            can_approve_leaves BOOLEAN DEFAULT 0,
            
            -- Departure permissions
            can_view_departures_list BOOLEAN DEFAULT 0,
            can_view_departure_details BOOLEAN DEFAULT 0,
            can_edit_departures_data BOOLEAN DEFAULT 0,
            can_add_new_departure BOOLEAN DEFAULT 0,
            can_delete_departure BOOLEAN DEFAULT 0,
            can_view_departures BOOLEAN DEFAULT 0,
            can_add_departures BOOLEAN DEFAULT 0,
            can_edit_departures BOOLEAN DEFAULT 0,
            can_delete_departures BOOLEAN DEFAULT 0,
            can_convert_departures BOOLEAN DEFAULT 0,
            
            -- Transfer permissions
            can_view_transfers_list BOOLEAN DEFAULT 0,
            can_view_transfer_details BOOLEAN DEFAULT 0,
            can_edit_transfers_data BOOLEAN DEFAULT 0,
            can_add_new_transfer BOOLEAN DEFAULT 0,
            can_delete_transfer BOOLEAN DEFAULT 0,
            
            -- Report permissions (بدون تكرار)
            can_view_employee_reports BOOLEAN DEFAULT 0,
            can_view_school_reports BOOLEAN DEFAULT 0,
            can_view_comprehensive_reports BOOLEAN DEFAULT 0,
            can_view_leave_reports BOOLEAN DEFAULT 0,
            can_view_departure_reports BOOLEAN DEFAULT 0,
            
            -- Export permissions
            can_export_employee_data BOOLEAN DEFAULT 0,
            can_export_school_data BOOLEAN DEFAULT 0,
            can_export_report_data BOOLEAN DEFAULT 0,
            can_export_employees BOOLEAN DEFAULT 0,
            can_export_leaves BOOLEAN DEFAULT 0,
            can_export_departures BOOLEAN DEFAULT 0,
            can_export_balances BOOLEAN DEFAULT 0,
            can_export_reports BOOLEAN DEFAULT 0,
            
            -- User management permissions
            can_view_users_list BOOLEAN DEFAULT 0,
            can_add_new_user BOOLEAN DEFAULT 0,
            can_manage_user_permissions BOOLEAN DEFAULT 0,
            
            -- Form permissions
            can_view_forms_list BOOLEAN DEFAULT 0,
            can_edit_forms_data BOOLEAN DEFAULT 0,
            can_add_new_form BOOLEAN DEFAULT 0,
            can_delete_form BOOLEAN DEFAULT 0,
            
            -- System permissions (بدون تكرار)
            can_view_system_logs BOOLEAN DEFAULT 0,
            can_manage_system_settings BOOLEAN DEFAULT 0,
            can_process_monthly_departures BOOLEAN DEFAULT 0,
            can_view_statistics BOOLEAN DEFAULT 0,
            
            -- Employee detailed permissions
            can_view_employees BOOLEAN DEFAULT 0,
            can_add_employees BOOLEAN DEFAULT 0,
            can_edit_employees BOOLEAN DEFAULT 0,
            can_delete_employees BOOLEAN DEFAULT 0,
            
            -- Special permissions
            can_view_own_school_only BOOLEAN DEFAULT 0
        )
        """)
        
        # نسخ البيانات من الجدول القديم
        cursor.execute("""
        INSERT INTO user_new 
        SELECT 
            id, username, password_hash, full_name, is_admin, created_at, can_backup_database,
            can_view_employees_list, can_view_employee_details, can_edit_employees_data, 
            can_add_new_employee, can_delete_employee,
            can_view_schools_list, can_view_school_details, can_edit_schools_data, 
            can_add_new_school, can_delete_school,
            can_view_leaves_list, can_view_leave_details, can_edit_leaves_data, 
            can_add_new_leave, can_delete_leave, can_manage_leave_balances,
            can_delete_leaves, can_approve_leaves,
            can_view_departures_list, can_view_departure_details, can_edit_departures_data,
            can_add_new_departure, can_delete_departure, can_view_departures,
            can_add_departures, can_edit_departures, can_delete_departures, can_convert_departures,
            can_view_transfers_list, can_view_transfer_details, can_edit_transfers_data,
            can_add_new_transfer, can_delete_transfer,
            can_view_employee_reports, can_view_school_reports, can_view_comprehensive_reports,
            can_view_leave_reports, can_view_departure_reports,
            can_export_employee_data, can_export_school_data, can_export_report_data,
            can_export_employees, can_export_leaves, can_export_departures, 
            can_export_balances, can_export_reports,
            can_view_users_list, can_add_new_user, can_manage_user_permissions,
            can_view_forms_list, can_edit_forms_data, can_add_new_form, can_delete_form,
            can_view_system_logs, can_manage_system_settings, can_process_monthly_departures,
            can_view_statistics, can_view_employees, can_add_employees, can_edit_employees,
            can_delete_employees, can_view_own_school_only
        FROM user
        """)
        
        # حذف الجدول القديم
        cursor.execute("DROP TABLE user")
        
        # إعادة تسمية الجدول الجديد
        cursor.execute("ALTER TABLE user_new RENAME TO user")
        
        conn.commit()
        print("تم إصلاح بنية قاعدة البيانات بنجاح!")
        
    except sqlite3.Error as e:
        print(f"خطأ في قاعدة البيانات: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_database_schema()