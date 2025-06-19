from app import app
from database import db
from models import Penalty

def add_penalties_table():
    """إضافة جدول العقوبات إلى قاعدة البيانات"""
    with app.app_context():
        try:
            # إنشاء الجدول
            db.create_all()
            print("تم إنشاء جدول العقوبات بنجاح")
        except Exception as e:
            print(f"خطأ في إنشاء الجدول: {str(e)}")

if __name__ == '__main__':
    add_penalties_table()