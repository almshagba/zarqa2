import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create SQLAlchemy base
Base = declarative_base()

# Define Employee model
class Employee(Base):
    __tablename__ = 'employees'
    
    id = Column(Integer, primary_key=True)
    employee_number = Column(String(50), unique=True)
    name = Column(String(100))
    position = Column(String(100))
    department = Column(String(100))
    hire_date = Column(Date)
    phone = Column(String(20))
    email = Column(String(100))

def validate_excel_structure(df):
    required_columns = ['رقم الموظف', 'الاسم', 'المنصب', 'القسم', 'تاريخ التعيين', 'رقم الهاتف', 'البريد الإلكتروني']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"الأعمدة التالية مفقودة في ملف الإكسل: {', '.join(missing_columns)}")
        return False
    return True

def import_excel_data(file_path):
    try:
        print(f"جاري قراءة الملف: {file_path}")
        
        # Check if file exists
        if not os.path.exists(file_path):
            print("خطأ: الملف غير موجود!")
            return
            
        # Read Excel file
        try:
            df = pd.read_excel(file_path)
            print(f"تم قراءة الملف بنجاح. عدد السجلات: {len(df)}")
        except Exception as e:
            print(f"خطأ في قراءة ملف الإكسل: {str(e)}")
            return
            
        # Validate Excel structure
        if not validate_excel_structure(df):
            return
            
        # Create database engine
        print("جاري إنشاء قاعدة البيانات...")
        engine = create_engine('sqlite:///employees.db')
        
        # Create tables
        Base.metadata.create_all(engine)
        print("تم إنشاء جداول قاعدة البيانات بنجاح")
        
        # Create session
        Session = sessionmaker(bind=engine)
        session = Session()
        
        print("جاري معالجة البيانات...")
        # Process each row in the Excel file
        for index, row in df.iterrows():
            try:
                employee = Employee(
                    employee_number=str(row['رقم الموظف']),
                    name=str(row['الاسم']),
                    position=str(row['المنصب']),
                    department=str(row['القسم']),
                    hire_date=pd.to_datetime(row['تاريخ التعيين']).date(),
                    phone=str(row['رقم الهاتف']),
                    email=str(row['البريد الإلكتروني'])
                )
                session.add(employee)
                print(f"تمت إضافة الموظف: {employee.name}")
            except Exception as e:
                print(f"خطأ في معالجة السطر {index + 1}: {str(e)}")
                session.rollback()
                continue
        
        # Commit changes
        try:
            session.commit()
            print("تم حفظ جميع البيانات بنجاح!")
        except Exception as e:
            print(f"خطأ في حفظ البيانات: {str(e)}")
            session.rollback()
    except Exception as e:
        print(f"خطأ غير متوقع: {str(e)}")
    finally:
        if 'session' in locals():
            session.close()

if __name__ == "__main__":
    while True:
        excel_file = input("الرجاء إدخال مسار ملف الإكسل (أو اكتب 'خروج' للإنهاء): ")
        if excel_file.lower() in ['خروج', 'exit', 'quit']:
            break
        import_excel_data(excel_file) 