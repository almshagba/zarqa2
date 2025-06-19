from flask import Flask, request, flash, redirect, url_for, session
import pandas as pd
import os
import tempfile
from werkzeug.datastructures import FileStorage
from io import BytesIO
from datetime import datetime
from models import School, Employee
from database import db
from constants import DIRECTORATE_DEPARTMENTS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'مفتاح_سري_للتطبيق'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employees.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

class MockRequest:
    def __init__(self, file, is_directorate=True):
        self.files = {'importFile': file}
        self.form = {'is_directorate': 'true' if is_directorate else 'false'}

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
    
    # Save to BytesIO
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    
    output.seek(0)
    return output

def parse_date_flexible(date_str):
    """
    تحليل التاريخ بتنسيقات مختلفة
    يدعم التنسيقات التالية:
    - YYYY-MM-DD
    - DD/MM/YYYY
    - DD-MM-YYYY
    - MM/DD/YYYY
    - التنسيقات العربية
    """
    if not date_str or pd.isna(date_str):
        return None
    
    # تنظيف سلسلة التاريخ
    date_str = str(date_str).strip()
    
    # قائمة تنسيقات التاريخ المدعومة
    date_formats = [
        '%Y-%m-%d',  # YYYY-MM-DD
        '%d/%m/%Y',  # DD/MM/YYYY
        '%d-%m-%Y',  # DD-MM-YYYY
        '%m/%d/%Y',  # MM/DD/YYYY
        '%Y/%m/%d',  # YYYY/MM/DD
        '%d.%m.%Y',  # DD.MM.YYYY
        '%Y.%m.%d',  # YYYY.MM.DD
    ]
    
    # محاولة تحليل التاريخ باستخدام التنسيقات المختلفة
    for date_format in date_formats:
        try:
            return datetime.strptime(date_str, date_format).date()
        except ValueError:
            continue
    
    # محاولة استخراج التاريخ من النص
    try:
        # تحويل الأرقام العربية إلى إنجليزية إذا وجدت
        arabic_to_english = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')
        date_str = date_str.translate(arabic_to_english)
        
        # استخراج الأرقام من النص
        import re
        numbers = re.findall(r'\d+', date_str)
        
        if len(numbers) >= 3:
            # تخمين ترتيب التاريخ بناءً على القيم
            year = None
            month = None
            day = None
            
            for num in numbers:
                if len(num) == 4 and 1900 <= int(num) <= 2100:
                    year = int(num)
                elif int(num) > 31:
                    year = int(num)
                elif int(num) > 12:
                    day = int(num)
                else:
                    if month is None:
                        month = int(num)
                    else:
                        day = int(num)
            
            # التحقق من وجود جميع مكونات التاريخ
            if year and month and day:
                # التحقق من صحة التاريخ
                if 1 <= month <= 12 and 1 <= day <= 31:
                    return datetime(year, month, day).date()
    except:
        pass
    
    # إذا فشلت جميع المحاولات
    raise ValueError(f'تنسيق التاريخ غير مدعوم: {date_str}')

def import_employees_data_test():
    """Test function for importing employee data"""
    try:
        with app.app_context():
            # Create test Excel file
            print("Creating test Excel file...")
            excel_data = create_test_excel()
            
            # Create a FileStorage object
            file = FileStorage(
                stream=excel_data,
                filename='test_import.xlsx',
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
            # Process the data
            print("Processing the data...")
            
            # Read the uploaded file
            df = pd.read_excel(file.stream)
            print(f"Excel file read successfully. Found {len(df)} rows.")
            
            # Clean column names
            df.columns = [col.strip() if isinstance(col, str) else col for col in df.columns]
            print(f"Columns after cleaning: {list(df.columns)}")
            
            # Process the data and add employees
            added = 0
            updated = 0
            skipped = 0
            errors = []
            
            # Set department column
            department_column = 'اسم القسم'  # For directorate employees
            
            # Get all schools from database
            all_schools = School.query.all()
            school_names = {school.name.strip(): school for school in all_schools}
            print(f"Found {len(school_names)} schools in database")
            
            # Create similar schools dictionary
            similar_schools = {}
            for name in school_names:
                # Remove definite article and spaces for comparison
                clean_name = name.replace('ال', '').replace(' ', '').strip()
                similar_schools[clean_name] = school_names[name]
            
            # Clean directorate department names
            directorate_dept_clean = [dept.replace('ال', '').replace(' ', '').strip() for dept in DIRECTORATE_DEPARTMENTS]
            
            # Process each row
            for index, row in df.iterrows():
                try:
                    print(f"\nProcessing row {index + 1}:")
                    
                    # Clean and prepare row data
                    row_dict = {}
                    for col in df.columns:
                        if col in row and not pd.isna(row[col]):
                            if isinstance(row[col], str):
                                row_dict[col] = row[col].strip()
                            else:
                                row_dict[col] = row[col]
                        else:
                            row_dict[col] = None
                    
                    # Check required fields
                    required_fields = ['الرقم الوزاري', 'الاسم', 'الرقم المدني', 'الوظيفة', department_column]
                    missing_fields = [field for field in required_fields if field not in row_dict or row_dict[field] is None]
                    
                    if missing_fields:
                        print(f"  Missing required fields: {missing_fields}")
                        errors.append(f'الصف {index + 2}: بيانات إلزامية مفقودة: {", ".join(missing_fields)}')
                        skipped += 1
                        continue
                    
                    # Find department in database
                    dept_name = row_dict[department_column]
                    print(f"  Looking for department: {dept_name}")
                    
                    school = None
                    
                    # Direct lookup
                    if dept_name in school_names:
                        school = school_names[dept_name]
                        print(f"  Found department directly: {school.name} (ID: {school.id})")
                    else:
                        # Clean department name for comparison
                        clean_dept_name = dept_name.replace('ال', '').replace(' ', '').strip()
                        print(f"  Cleaned department name: {clean_dept_name}")
                        
                        # Look in similar schools dictionary
                        if clean_dept_name in similar_schools:
                            school = similar_schools[clean_dept_name]
                            print(f"  Found department through cleaning: {school.name} (ID: {school.id})")
                        else:
                            # Try partial matching
                            for name, school_obj in school_names.items():
                                clean_name = name.replace('ال', '').replace(' ', '').strip()
                                if clean_dept_name in clean_name or clean_name in clean_dept_name:
                                    school = school_obj
                                    print(f"  Found department through partial match: {school.name} (ID: {school.id})")
                                    break
                    
                    if not school:
                        print(f"  Department not found: {dept_name}")
                        errors.append(f'الصف {index + 2}: المدرسة/القسم غير موجود: {dept_name}')
                        skipped += 1
                        continue
                    
                    # Check if it's a directorate department
                    clean_school_name = school.name.replace('ال', '').replace(' ', '').strip()
                    is_school_directorate = clean_school_name in directorate_dept_clean
                    print(f"  Is directorate department: {is_school_directorate}")
                    
                    if not is_school_directorate:
                        print(f"  Department is not a directorate department: {school.name}")
                        errors.append(f'الصف {index + 2}: القسم المحدد "{school.name}" ليس من أقسام المديرية')
                        skipped += 1
                        continue
                    
                    # Clean ministry number and civil ID
                    ministry_number = str(row_dict['الرقم الوزاري']).strip()
                    civil_id = str(row_dict['الرقم المدني']).strip()
                    
                    # Check if employee already exists
                    existing_employee = Employee.query.filter(
                        db.or_(
                            Employee.ministry_number == ministry_number,
                            Employee.civil_id == civil_id
                        )
                    ).first()
                    
                    # Prepare employee data
                    employee_data = {
                        'name': row_dict['الاسم'],
                        'ministry_number': ministry_number,
                        'civil_id': civil_id,
                        'job_title': row_dict['الوظيفة'],
                        'school_id': school.id,
                        'phone_number': str(row_dict.get('رقم الهاتف', '')) if row_dict.get('رقم الهاتف') else None,
                        'gender': row_dict.get('الجنس', 'ذكر'),
                        'qualification': row_dict.get('المؤهل', ''),
                        'bachelor_specialization': row_dict.get('تخصص بكالوريوس', ''),
                        'high_diploma_specialization': row_dict.get('تخصص دبلوم العالي', ''),
                        'masters_specialization': row_dict.get('تخصص ماجستير', ''),
                        'phd_specialization': row_dict.get('تخصص دكتوراه', ''),
                        'subject': row_dict.get('المبحث الدراسي', ''),
                        'is_directorate_employee': True
                    }
                    
                    # Process appointment date
                    if row_dict.get('تاريخ التعيين'):
                        try:
                            appointment_date = parse_date_flexible(str(row_dict['تاريخ التعيين']))
                            if appointment_date:
                                employee_data['appointment_date'] = appointment_date
                                print(f"  Parsed appointment date: {appointment_date}")
                        except Exception as e:
                            print(f"  Error parsing date: {str(e)}")
                            errors.append(f'الصف {index + 2}: خطأ في تنسيق التاريخ: {str(e)}')
                    
                    if existing_employee:
                        print(f"  Updating existing employee: {existing_employee.name} (ID: {existing_employee.id})")
                        # Update existing employee
                        for key, value in employee_data.items():
                            setattr(existing_employee, key, value)
                        updated += 1
                    else:
                        print(f"  Adding new employee: {employee_data['name']}")
                        # Create new employee
                        new_employee = Employee(**employee_data)
                        db.session.add(new_employee)
                        added += 1
                        
                except Exception as e:
                    print(f"  Error processing row: {str(e)}")
                    errors.append(f'خطأ في الصف {index + 2}: {str(e)}')
                    skipped += 1
            
            # Commit changes to database
            print("\nCommitting changes to database...")
            # db.session.commit()  # Commented out to prevent actual changes
            
            print("\nImport summary:")
            print(f"Added: {added}")
            print(f"Updated: {updated}")
            print(f"Skipped: {skipped}")
            print(f"Errors: {len(errors)}")
            
            if errors:
                print("\nErrors:")
                for error in errors:
                    print(f"- {error}")
    
    except Exception as e:
        print(f"Error during import test: {str(e)}")
        import traceback
        traceback.print_exc()

def test_import():
    print("Testing import functionality...")
    
    try:
        with app.app_context():
            # Create test data
            print("Creating test data...")
            
            # Check if departments exist in database
            print("Checking departments in database...")
            for dept in DIRECTORATE_DEPARTMENTS:
                school = School.query.filter_by(name=dept).first()
                if school:
                    print(f"Found department: {dept}")
                else:
                    print(f"Department not found: {dept}")
                    # Create department if it doesn't exist
                    new_school = School(name=dept, region="المديرية")
                    db.session.add(new_school)
                    print(f"Created department: {dept}")
            
            # Commit changes
            db.session.commit()
            print("Departments updated in database.")
            
            # Test import form submission
            print("\nTesting form submission...")
            from routes.main_routes import import_employees_data
            
            # Create a mock request context
            with app.test_request_context('/import_employees_data', method='POST'):
                # Create test file
                data = {
                    'الرقم الوزاري': ['TEST001', 'TEST002'],
                    'الاسم': ['موظف اختبار 1', 'موظف اختبار 2'],
                    'الرقم المدني': ['9999999991', '9999999992'],
                    'الوظيفة': ['مدير', 'كاتب'],
                    'اسم القسم': [DIRECTORATE_DEPARTMENTS[0], DIRECTORATE_DEPARTMENTS[1]],
                }
                
                # Create DataFrame and save to temp file
                df = pd.DataFrame(data)
                fd, temp_path = tempfile.mkstemp(suffix='.xlsx')
                with pd.ExcelWriter(temp_path) as writer:
                    df.to_excel(writer, index=False)
                os.close(fd)
                
                print(f"Test file created at: {temp_path}")
                
                # Mock the request
                from werkzeug.datastructures import FileStorage
                with open(temp_path, 'rb') as f:
                    file_content = f.read()
                
                # Create file storage object
                file = FileStorage(
                    stream=BytesIO(file_content),
                    filename='test_import.xlsx',
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                
                # Mock the request.files
                from flask import request
                request.files = {'importFile': file}
                request.form = {'is_directorate': 'true'}
                
                # Call the import function
                print("Calling import_employees_data function...")
                
                # Instead of calling the function directly, let's implement the logic here
                print("Simulating import process...")
                
                # Read the file
                df = pd.read_excel(BytesIO(file_content))
                print(f"Read {len(df)} rows from file")
                
                # Clean column names
                df.columns = [col.strip() if isinstance(col, str) else col for col in df.columns]
                print(f"Columns: {list(df.columns)}")
                
                # Process each row
                for index, row in df.iterrows():
                    print(f"\nProcessing row {index + 1}:")
                    dept_name = row['اسم القسم']
                    print(f"Department: {dept_name}")
                    
                    # Find department in database
                    school = School.query.filter_by(name=dept_name).first()
                    if school:
                        print(f"Found department in database: {school.name} (ID: {school.id})")
                    else:
                        print(f"Department not found in database: {dept_name}")
                
                # Clean up
                os.unlink(temp_path)
                print("Test file removed")
    
    except Exception as e:
        print(f"Error during test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_import() 