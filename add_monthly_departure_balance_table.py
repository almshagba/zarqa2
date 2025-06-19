from app import app
from database import db
from models import MonthlyDepartureBalance

with app.app_context():
    # إنشاء جدول MonthlyDepartureBalance
    db.create_all()
    print("تم إنشاء جدول MonthlyDepartureBalance بنجاح")