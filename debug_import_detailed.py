from flask import Flask, session, request
import pandas as pd
from io import BytesIO
from datetime import datetime
import os
import tempfile
from models import School, Employee
from database import db
from constants import DIRECTORATE_DEPARTMENTS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'مفتاح_سري_للتطبيق'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employees.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def create_test_excel():
    """Create a test Excel file with directorate employee data"""
    # Create test data
    data = {
        'الرقم الوزاري': ['TEST001', 'TEST002', 'TEST003'],
        'الاسم': ['موظف اختبار 1', 'موظف اختبار 2', 'موظف اختبار 3'],
        'الرقم المدني': ['9999999991', '9999999992', '9999999993'],
        'الوظيفة': ['مدير', 'كاتب', 'محاسب'],
        'اسم القسم': [DIRECTORATE_DEPARTMENTS[0], DIRECTORATE_DEPARTMENTS[1], DIRECTORATE_DEPARTMENTS[2]],
        'الجنس': ['ذكر', 'ذكر', 'ذكر'],
        'المؤهل': ['بكالوريوس', 'بكالوريوس', 'بكالوريوس'],
        'تاريخ التعيين': ['2023-01-01', '2023-02-01', '2023-03-01'],
        'رقم الهاتف': ['0501234567', '0502345678', '0503456789']
    }
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save to temporary file
    fd, path = tempfile.mkstemp(suffix='.xlsx')
    with pd.ExcelWriter(path) as writer:
        df.to_excel(writer, index=False)
    
    os.close(fd)
    return path

def debug_import_function():
    print("Starting detailed import debugging...")
    
    try:
        with app.app_context():
            # Check if directorate departments exist in the database
            print("Checking directorate departments in database...")
            for dept in DIRECTORATE_DEPARTMENTS:
                school = School.query.filter_by(name=dept).first()
                if school:
                    print(f"Found department: {dept} (ID: {school.id})")
                else:
                    print(f"Department not found in database: {dept}")
            
            # Create test Excel file
            print("\nCreating test Excel file...")
            test_file_path = create_test_excel()
            print(f"Test file created at: {test_file_path}")
            
            # Simulate import process
            print("\nSimulating import process...")
            
            # Read the test file
            df = pd.read_excel(test_file_path)
            print(f"Excel file read successfully. Found {len(df)} rows.")
            
            # Clean column names
            df.columns = [col.strip() if isinstance(col, str) else col for col in df.columns]
            print(f"Columns after cleaning: {list(df.columns)}")
            
            # Process each row
            for index, row in df.iterrows():
                print(f"\nProcessing row {index + 1}:")
                
                # Extract required fields
                ministry_number = str(row['الرقم الوزاري']).strip()
                name = str(row['الاسم']).strip()
                civil_id = str(row['الرقم المدني']).strip()
                job_title = str(row['الوظيفة']).strip()
                dept_name = str(row['اسم القسم']).strip()
                
                print(f"  Ministry Number: {ministry_number}")
                print(f"  Name: {name}")
                print(f"  Civil ID: {civil_id}")
                print(f"  Job Title: {job_title}")
                print(f"  Department: {dept_name}")
                
                # Find department in database
                school = School.query.filter_by(name=dept_name).first()
                if school:
                    print(f"  Department found in database: {school.name} (ID: {school.id})")
                else:
                    print(f"  Department not found in database: {dept_name}")
                    
                    # Try approximate matching
                    print("  Attempting approximate matching...")
                    all_schools = School.query.all()
                    school_names = {school.name.strip(): school for school in all_schools}
                    
                    # Create similar schools dictionary
                    similar_schools = {}
                    for name in school_names:
                        clean_name = name.replace('ال', '').replace(' ', '').strip()
                        similar_schools[clean_name] = school_names[name]
                    
                    # Clean the department name
                    clean_dept_name = dept_name.replace('ال', '').replace(' ', '').strip()
                    
                    # Try to find a match
                    if clean_dept_name in similar_schools:
                        school = similar_schools[clean_dept_name]
                        print(f"  Found match through cleaning: {school.name} (ID: {school.id})")
                    else:
                        # Look for partial matches
                        for name, school_obj in school_names.items():
                            clean_name = name.replace('ال', '').replace(' ', '').strip()
                            if clean_dept_name in clean_name or clean_name in clean_dept_name:
                                school = school_obj
                                print(f"  Found partial match: {school.name} (ID: {school.id})")
                                break
                
                # Check if it's a directorate department
                if school:
                    is_directorate = school.name in DIRECTORATE_DEPARTMENTS
                    print(f"  Is directorate department: {is_directorate}")
                
            # Clean up
            os.unlink(test_file_path)
            print("\nTest file removed.")
            
    except Exception as e:
        print(f"Error during detailed import testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_import_function() 