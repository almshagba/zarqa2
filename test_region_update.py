from app import app
from database import db
from models import School

with app.app_context():
    try:
        # الحصول على أول مدرسة وتحديث منطقتها
        school = School.query.first()
        if school:
            print(f"المدرسة: {school.name}")
            print(f"المنطقة الحالية: {school.region}")
            
            # تحديث المنطقة
            school.region = "الهاشمية"
            db.session.commit()
            
            print(f"المنطقة الجديدة: {school.region}")
            print("تم التحديث بنجاح")
        else:
            print("لا توجد مدارس في قاعدة البيانات")
            
    except Exception as e:
        print(f"حدث خطأ: {e}")
        db.session.rollback()