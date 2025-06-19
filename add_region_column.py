from app import app, db
from sqlalchemy import text

with app.app_context():
    # إضافة عمود المنطقة إلى جدول المدارس
    try:
        db.session.execute(text('ALTER TABLE school ADD COLUMN region VARCHAR(50)'))
        db.session.commit()
        print("تم إضافة عمود المنطقة بنجاح")
    except Exception as e:
        print(f"حدث خطأ: {e}")