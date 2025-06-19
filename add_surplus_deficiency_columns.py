from app import app
from database import db
from sqlalchemy import text

def add_surplus_deficiency_columns():
    """إضافة حقول النواقص والزوائد الجديدة"""
    with app.app_context():
        try:
            # إضافة الحقول الجديدة
            db.session.execute(text("""
                ALTER TABLE technical_deficiencies 
                ADD COLUMN deficiency_bachelor INTEGER DEFAULT 0
            """))
            
            db.session.execute(text("""
                ALTER TABLE technical_deficiencies 
                ADD COLUMN deficiency_diploma INTEGER DEFAULT 0
            """))
            
            db.session.execute(text("""
                ALTER TABLE technical_deficiencies 
                ADD COLUMN surplus_bachelor INTEGER DEFAULT 0
            """))
            
            db.session.execute(text("""
                ALTER TABLE technical_deficiencies 
                ADD COLUMN surplus_diploma INTEGER DEFAULT 0
            """))
            
            db.session.commit()
            print("تم إضافة حقول النواقص والزوائد بنجاح")
            
        except Exception as e:
            print(f"خطأ في إضافة الحقول: {e}")
            db.session.rollback()

if __name__ == '__main__':
    add_surplus_deficiency_columns()