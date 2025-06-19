from app import app
from models import db, School

with app.app_context():
    # البحث عن أول مدرسة وتحديث منطقتها
    school = School.query.first()
    if school:
        school.region = "الهاشمية"
        db.session.commit()
        print(f"تم تحديث منطقة المدرسة {school.name} إلى {school.region}")
    else:
        print("لا توجد مدارس في قاعدة البيانات")
    
    # عرض جميع المدارس ومناطقها
    schools = School.query.all()
    print("\nقائمة المدارس ومناطقها:")
    for school in schools:
        print(f"{school.name}: {school.region or 'غير محدد'}")