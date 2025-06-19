from app import app
from database import db
from models import LeaveBalance
from sqlalchemy import text

def add_leave_balance_table():
    with app.app_context():
        try:
            # إنشاء الجدول الجديد
            db.create_all()
            print("تم إنشاء جدول رصيد الإجازات بنجاح")
        except Exception as e:
            print(f"خطأ في إنشاء الجدول: {e}")
            db.session.rollback()

if __name__ == '__main__':
    add_leave_balance_table()