from app import app, db
from sqlalchemy import text

# تحديث جدول Leave لإضافة أعمدة المغادرات
def upgrade_db():
    with app.app_context():
        # إنشاء اتصال مباشر بقاعدة البيانات
        with db.engine.connect() as conn:
            # إضافة عمود وقت البداية
            conn.execute(text('ALTER TABLE leave ADD COLUMN start_time TIME'))
            # إضافة عمود وقت النهاية
            conn.execute(text('ALTER TABLE leave ADD COLUMN end_time TIME'))
            # إضافة عمود عدد الساعات
            conn.execute(text('ALTER TABLE leave ADD COLUMN hours_count FLOAT'))
            # تنفيذ التغييرات
            conn.commit()
        
        print("تم تحديث قاعدة البيانات بنجاح")

if __name__ == '__main__':
    upgrade_db()