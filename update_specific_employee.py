from app import app
from models import Employee, School
from database import db

def fix_daheem_employee():
    with app.app_context():
        # البحث عن المدرسة
        school_names = ["الدهيم الأساسية المختلطة", "الدهيثم الاساسيه المختلطه"]
        
        for school_name in school_names:
            school = School.query.filter_by(name=school_name).first()
            if school:
                # البحث عن الموظفين في هذه المدرسة
                employees = Employee.query.filter_by(school_id=school.id).all()
                
                for employee in employees:
                    if employee.is_directorate_employee:
                        print(f"تم العثور على موظف مدرسة مصنف خطأً كموظف مديرية: {employee.name} - {employee.ministry_number}")
                        employee.is_directorate_employee = False
                        print(f"تم تصحيح حالة الموظف: {employee.name}")
                
                db.session.commit()
                print(f"تم تصحيح حالة الموظفين في مدرسة: {school_name}")

if __name__ == "__main__":
    fix_daheem_employee()