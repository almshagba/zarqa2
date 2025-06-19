from database import db
from app import app

def add_detailed_permissions():
    with app.app_context():
        # إضافة الأعمدة الجديدة للصلاحيات المفصلة
        try:
            db.engine.execute('''
                ALTER TABLE user ADD COLUMN can_view_employees BOOLEAN DEFAULT 0;
                ALTER TABLE user ADD COLUMN can_add_employees BOOLEAN DEFAULT 0;
                ALTER TABLE user ADD COLUMN can_edit_employees BOOLEAN DEFAULT 0;
                ALTER TABLE user ADD COLUMN can_delete_employees BOOLEAN DEFAULT 0;
                ALTER TABLE user ADD COLUMN can_view_employee_details BOOLEAN DEFAULT 0;
                
                ALTER TABLE user ADD COLUMN can_view_leaves BOOLEAN DEFAULT 0;
                ALTER TABLE user ADD COLUMN can_add_leaves BOOLEAN DEFAULT 0;
                ALTER TABLE user ADD COLUMN can_edit_leaves BOOLEAN DEFAULT 0;
                ALTER TABLE user ADD COLUMN can_delete_leaves BOOLEAN DEFAULT 0;
                ALTER TABLE user ADD COLUMN can_approve_leaves BOOLEAN DEFAULT 0;
                ALTER TABLE user ADD COLUMN can_manage_leave_balances BOOLEAN DEFAULT 0;
                
                ALTER TABLE user ADD COLUMN can_view_departures BOOLEAN DEFAULT 0;
                ALTER TABLE user ADD COLUMN can_add_departures BOOLEAN DEFAULT 0;
                ALTER TABLE user ADD COLUMN can_edit_departures BOOLEAN DEFAULT 0;
                ALTER TABLE user ADD COLUMN can_delete_departures BOOLEAN DEFAULT 0;
                ALTER TABLE user ADD COLUMN can_convert_departures BOOLEAN DEFAULT 0;
                
                ALTER TABLE user ADD COLUMN can_view_employee_reports BOOLEAN DEFAULT 0;
                ALTER TABLE user ADD COLUMN can_view_school_reports BOOLEAN DEFAULT 0;
                ALTER TABLE user ADD COLUMN can_view_leave_reports BOOLEAN DEFAULT 0;
                ALTER TABLE user ADD COLUMN can_view_departure_reports BOOLEAN DEFAULT 0;
                ALTER TABLE user ADD COLUMN can_view_comprehensive_reports BOOLEAN DEFAULT 0;
                
                ALTER TABLE user ADD COLUMN can_export_employees BOOLEAN DEFAULT 0;
                ALTER TABLE user ADD COLUMN can_export_leaves BOOLEAN DEFAULT 0;
                ALTER TABLE user ADD COLUMN can_export_departures BOOLEAN DEFAULT 0;
                ALTER TABLE user ADD COLUMN can_export_balances BOOLEAN DEFAULT 0;
                ALTER TABLE user ADD COLUMN can_export_reports BOOLEAN DEFAULT 0;
                
                ALTER TABLE user ADD COLUMN can_view_system_logs BOOLEAN DEFAULT 0;
                ALTER TABLE user ADD COLUMN can_manage_system_settings BOOLEAN DEFAULT 0;
                ALTER TABLE user ADD COLUMN can_view_statistics BOOLEAN DEFAULT 0;
                
                ALTER TABLE user ADD COLUMN can_view_own_school_only BOOLEAN DEFAULT 0;
                ALTER TABLE user ADD COLUMN can_manage_school_employees BOOLEAN DEFAULT 0;
                ALTER TABLE user ADD COLUMN can_view_school_statistics BOOLEAN DEFAULT 0;
            ''')
            
            print("تم إضافة الصلاحيات المفصلة بنجاح!")
            
        except Exception as e:
            print(f"خطأ في إضافة الصلاحيات: {e}")

if __name__ == '__main__':
    add_detailed_permissions()