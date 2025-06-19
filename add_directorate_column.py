from app import app, db
from sqlalchemy import text

with app.app_context():
    # إضافة العمود is_directorate_employee إلى جدول employee
    db.session.execute(text("ALTER TABLE employee ADD COLUMN is_directorate_employee BOOLEAN DEFAULT 0"))
    db.session.commit()
    print("تم إضافة عمود is_directorate_employee بنجاح")