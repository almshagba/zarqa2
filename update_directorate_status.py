from app import app
from database import db
from models import Employee, School
from constants import DIRECTORATE_DEPARTMENTS

with app.app_context():
    # أولاً: تعيين جميع الموظفين كموظفي مدارس (False)
    Employee.query.update({Employee.is_directorate_employee: False})
    
    # ثانياً: الحصول على معرفات أقسام المديرية
    directorate_school_ids = db.session.query(School.id).filter(
        School.name.in_(DIRECTORATE_DEPARTMENTS)
    ).all()
    
    # استخراج المعرفات فقط
    directorate_ids = [school_id[0] for school_id in directorate_school_ids]
    
    # ثالثاً: تحديث الموظفين الذين ينتمون لأقسام المديرية
    updated_count = Employee.query.filter(
        Employee.school_id.in_(directorate_ids)
    ).update(
        {Employee.is_directorate_employee: True},
        synchronize_session=False
    )
    
    db.session.commit()
    
    print(f"تم تحديث {updated_count} موظف كموظفي مديرية")
    
    # طباعة إحصائيات
    directorate_employees = Employee.query.filter_by(is_directorate_employee=True).count()
    school_employees = Employee.query.filter_by(is_directorate_employee=False).count()
    
    print(f"إجمالي موظفي المديرية: {directorate_employees}")
    print(f"إجمالي موظفي المدارس: {school_employees}")
    print("تم التحديث بنجاح!")