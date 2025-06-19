from app import app
from database import db
from models import User

with app.app_context():
    # إضافة العمود الجديد
    try:
        db.engine.execute('ALTER TABLE user ADD COLUMN can_backup_database BOOLEAN DEFAULT 0')
        print("تم إضافة صلاحية النسخ الاحتياطي بنجاح")
    except Exception as e:
        print(f"خطأ: {e}")