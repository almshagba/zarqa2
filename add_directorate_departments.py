from app import app, db
from models import School
from constants import DIRECTORATE_DEPARTMENTS

with app.app_context():
    # إضافة الأقسام كمدارس في قاعدة البيانات
    for department_name in DIRECTORATE_DEPARTMENTS:
        # التحقق من عدم وجود القسم مسبقاً
        existing_department = School.query.filter_by(name=department_name).first()
        if not existing_department:
            department = School(
                name=department_name,
                gender="مختلطة",  # افتراضي
                address="مديرية التربية والتعليم",
                phone=""
            )
            db.session.add(department)
            print(f"تمت إضافة القسم: {department_name}")
    
    db.session.commit()
    print("تم إضافة جميع الأقسام بنجاح")