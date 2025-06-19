from app import app
from database import db
from models import ConvertedDeparture

with app.app_context():
    # إنشاء جدول المغادرات المحولة
    db.create_all()
    print("تم إنشاء جدول المغادرات المحولة بنجاح")