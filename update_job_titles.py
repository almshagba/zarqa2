from app import app
from models import Employee
from database import db
from constants import JOB_TITLES

# تعيين الوظيفة الافتراضية للموظفين الذين لديهم وظائف غير موجودة في القائمة
DEFAULT_JOB = "معلم"

def update_job_titles():
    with app.app_context():
        # الحصول على جميع الموظفين
        employees = Employee.query.all()
        
        # عدد الموظفين الذين تم تحديثهم
        updated_count = 0
        
        for employee in employees:
            # التحقق مما إذا كانت الوظيفة الحالية غير موجودة في القائمة
            if employee.job_title not in JOB_TITLES:
                print(f"تحديث وظيفة الموظف {employee.name} من '{employee.job_title}' إلى '{DEFAULT_JOB}'")
                employee.job_title = DEFAULT_JOB
                updated_count += 1
        
        # حفظ التغييرات إذا تم تحديث أي موظف
        if updated_count > 0:
            db.session.commit()
            print(f"تم تحديث وظائف {updated_count} موظف")
        else:
            print("لم يتم تحديث أي وظائف")

if __name__ == "__main__":
    update_job_titles()