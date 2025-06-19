from app import app, db
from models import Employee

# قائمة بالأرقام الوزارية لموظفي المديرية
directorate_ministry_numbers = [
    # أضف هنا الأرقام الوزارية لموظفي المديرية
    '12345', '67890', '54321'  # استبدل هذه بالأرقام الوزارية الحقيقية
]

with app.app_context():
    # تحديث الموظفين بناءً على الأرقام الوزارية
    for ministry_number in directorate_ministry_numbers:
        employee = Employee.query.filter_by(ministry_number=ministry_number).first()
        if employee:
            employee.is_directorate_employee = True
            print(f"تم تحديث الموظف: {employee.name}")
    
    # أو يمكنك تحديث موظفين محددين بناءً على معايير أخرى
    # مثال: تحديث الموظفين الذين يعملون في مدرسة معينة
    # employees = Employee.query.filter_by(school_id=1).all()
    # for employee in employees:
    #     employee.is_directorate_employee = True
    
    db.session.commit()
    print("تم تحديث موظفي المديرية بنجاح")