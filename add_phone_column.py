import sqlite3

# Connect to the database
conn = sqlite3.connect('instance/employees.db')
cursor = conn.cursor()

# Check if the column already exists
cursor.execute("PRAGMA table_info(employee)")
columns = cursor.fetchall()
column_names = [column[1] for column in columns]

if 'phone_number' not in column_names:
    # Add the phone_number column
    cursor.execute("ALTER TABLE employee ADD COLUMN phone_number TEXT")
    print("Added phone_number column to employee table")
else:
    print("phone_number column already exists")

# Commit the changes and close the connection
conn.commit()
conn.close()
from app import app
from database import db
from sqlalchemy import text

def upgrade_database():
    with app.app_context():
        # إضافة عمود رقم الهاتف إلى جدول الموظفين
        try:
            db.session.execute(text('ALTER TABLE employee ADD COLUMN phone_number VARCHAR(20)'))
            db.session.commit()
            print("تم إضافة عمود رقم الهاتف بنجاح")
        except Exception as e:
            print(f"حدث خطأ: {e}")
            db.session.rollback()

if __name__ == "__main__":
    upgrade_database()