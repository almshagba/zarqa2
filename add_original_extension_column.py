import sqlite3
from app import app
from database import db
from sqlalchemy import text

def upgrade_database():
    with app.app_context():
        # إضافة عمود الامتداد الأصلي إلى جدول النماذج
        try:
            db.session.execute(text('ALTER TABLE form_template ADD COLUMN original_extension VARCHAR(10)'))
            db.session.commit()
            print("Added original_extension column to form_template table")
        except Exception as e:
            print(f"Error adding original_extension column: {e}")
            db.session.rollback()

if __name__ == '__main__':
    # Connect to the database directly
    conn = sqlite3.connect('instance/employees.db')
    cursor = conn.cursor()
    
    # Check if the column already exists
    cursor.execute("PRAGMA table_info(form_template)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    
    if 'original_extension' not in column_names:
        # Add the original_extension column
        cursor.execute("ALTER TABLE form_template ADD COLUMN original_extension TEXT")
        print("Added original_extension column to form_template table")
    else:
        print("original_extension column already exists")
    
    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    
    # Also run the SQLAlchemy version
    upgrade_database()