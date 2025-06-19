import pandas as pd
import os
import tempfile
import pandas as pd
from datetime import datetime
from constants import DIRECTORATE_DEPARTMENTS

def create_test_excel():
    """Create a test Excel file for directorate employee import"""
    # Create test data
    data = {
        'الرقم الوزاري': ['TEST001', 'TEST002', 'TEST003'],
        'الاسم': ['موظف اختبار 1', 'موظف اختبار 2', 'موظف اختبار 3'],
        'الرقم المدني': ['9999999991', '9999999992', '9999999993'],
        'الوظيفة': ['مدير', 'كاتب', 'محاسب'],
        'اسم القسم': ['مدير تربية وتعليم', 'مدير شؤون ادارية ومالية', 'مدير شؤون تعليمية وفنية'],
        'الجنس': ['ذكر', 'ذكر', 'ذكر'],
        'المؤهل': ['بكالوريوس', 'بكالوريوس', 'بكالوريوس'],
        'تاريخ التعيين': ['2023-01-01', '2023-02-01', '2023-03-01'],
        'رقم الهاتف': ['0501234567', '0502345678', '0503456789']
    }
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save to file in the current directory
    file_path = 'test_directorate_import.xlsx'
    with pd.ExcelWriter(file_path) as writer:
        df.to_excel(writer, index=False)
    
    print(f"Test file created at: {file_path}")
    return file_path

def print_directorate_departments():
    """Print the list of directorate departments for reference"""
    print("\nDepartments defined in constants.py:")
    for i, dept in enumerate(DIRECTORATE_DEPARTMENTS, 1):
        print(f"{i}. {dept}")

def main():
    # Create a test Excel file
    print("Creating test Excel file for directorate employee import...")
    test_file_path = create_test_excel()
    
    # Print instructions
    print("\n" + "="*50)
    print("TEST INSTRUCTIONS:")
    print("="*50)
    print("1. Run the Flask application (python app.py)")
    print("2. Go to the directorate employees page")
    print("3. Click on 'استيراد موظفين' button")
    print("4. Upload the generated file:", test_file_path)
    print("5. Check if the employees are imported correctly")
    print("="*50)
    
    # Print the list of directorate departments
    print_directorate_departments()

if __name__ == "__main__":
    main()