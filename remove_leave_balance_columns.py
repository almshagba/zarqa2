from app import app
from database import db
from sqlalchemy import text

def remove_leave_balance_columns():
    with app.app_context():
        try:
            # حذف أعمدة رصيد الإجازات
            db.session.execute(text('ALTER TABLE employee DROP COLUMN current_year_leave_balance'))
            db.session.execute(text('ALTER TABLE employee DROP COLUMN previous_year_leave_balance'))
            db.session.execute(text('ALTER TABLE employee DROP COLUMN sick_leave_balance'))
            db.session.commit()
            print("تم حذف أعمدة رصيد الإجازات بنجاح")
        except Exception as e:
            print(f"خطأ في حذف الأعمدة: {e}")
            db.session.rollback()

if __name__ == '__main__':
    remove_leave_balance_columns()