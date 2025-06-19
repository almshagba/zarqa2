from database import db
from app import app

def add_user_permissions():
    with app.app_context():
        # إضافة الأعمدة الجديدة
        db.engine.execute('''
            ALTER TABLE user ADD COLUMN can_manage_employees BOOLEAN DEFAULT 0;
            ALTER TABLE user ADD COLUMN can_manage_schools BOOLEAN DEFAULT 0;
            ALTER TABLE user ADD COLUMN can_manage_leaves BOOLEAN DEFAULT 0;
            ALTER TABLE user ADD COLUMN can_manage_departures BOOLEAN DEFAULT 0;
            ALTER TABLE user ADD COLUMN can_manage_transfers BOOLEAN DEFAULT 0;
            ALTER TABLE user ADD COLUMN can_view_reports BOOLEAN DEFAULT 0;
            ALTER TABLE user ADD COLUMN can_export_data BOOLEAN DEFAULT 0;
            ALTER TABLE user ADD COLUMN can_manage_users BOOLEAN DEFAULT 0;
            ALTER TABLE user ADD COLUMN can_manage_forms BOOLEAN DEFAULT 0;
            ALTER TABLE user ADD COLUMN can_process_monthly_departures BOOLEAN DEFAULT 0;
        ''')
        
        print("تم إضافة حقول الصلاحيات بنجاح!")

if __name__ == '__main__':
    add_user_permissions()