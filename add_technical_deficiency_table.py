from app import app
from database import db
from models import TechnicalDeficiency

def create_technical_deficiency_table():
    """إنشاء جدول النقص الفني"""
    with app.app_context():
        try:
            # إنشاء الجدول
            db.create_all()
            print("تم إنشاء جدول النقص الفني بنجاح")
            
        except Exception as e:
            print(f"خطأ في إنشاء الجدول: {e}")
            db.session.rollback()

if __name__ == '__main__':
    create_technical_deficiency_table()