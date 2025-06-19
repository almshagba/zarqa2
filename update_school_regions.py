from app import app
from database import db
from models import School
from sqlalchemy import text

with app.app_context():
    # تحديث المناطق للمدارس الموجودة
    try:
        # الحصول على جميع المدارس
        schools = School.query.all()
        print(f"عدد المدارس الموجودة: {len(schools)}")
        
        # تحديث المناطق بناءً على أسماء المدارس أو تعيين منطقة افتراضية
        updated_count = 0
        for school in schools:
            if not school.region:  # إذا لم تكن المنطقة محددة
                # يمكن تحديد المنطقة بناءً على اسم المدرسة أو تعيين منطقة افتراضية
                if "الهاشمية" in school.name:
                    school.region = "الهاشمية"
                elif "بيرين" in school.name:
                    school.region = "بيرين"
                elif "الحلابات" in school.name:
                    school.region = "الحلابات"
                elif "الظليل" in school.name:
                    school.region = "الظليل"
                elif "الازرق" in school.name:
                    school.region = "الازرق"
                else:
                    # تعيين منطقة افتراضية للمدارس التي لا تحتوي على اسم منطقة
                    school.region = "الهاشمية"  # منطقة افتراضية
                
                updated_count += 1
                print(f"تم تحديث المدرسة: {school.name} -> المنطقة: {school.region}")
        
        # حفظ التغييرات
        db.session.commit()
        print(f"تم تحديث {updated_count} مدرسة بنجاح")
        
        # عرض المدارس مع مناطقها
        print("\nقائمة المدارس مع المناطق:")
        schools = School.query.all()
        for school in schools:
            print(f"{school.name}: {school.region or 'غير محدد'}")
            
    except Exception as e:
        print(f"حدث خطأ: {e}")
        db.session.rollback()