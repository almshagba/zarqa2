from app import app
from database import db
from sqlalchemy import text

def upgrade_database():
    with app.app_context():
        # إضافة عمود جنس المدرسة إلى جدول المدارس
        try:
            db.session.execute(text('ALTER TABLE school ADD COLUMN gender VARCHAR(20)'))
            db.session.commit()
            print("تم إضافة عمود جنس المدرسة بنجاح")
        except Exception as e:
            print(f"حدث خطأ: {e}")
            db.session.rollback()

if __name__ == "__main__":
    upgrade_database()