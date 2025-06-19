import pandas as pd
import os
import tempfile
from datetime import datetime

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
    
    # Save to temporary file
    fd, path = tempfile.mkstemp(suffix='.xlsx')
    with pd.ExcelWriter(path) as writer:
        df.to_excel(writer, index=False)
    
    os.close(fd)
    return path

def check_excel_file(file_path):
    """Check the content of an Excel file"""
    try:
        print(f"Reading Excel file: {file_path}")
        df = pd.read_excel(file_path)
        print(f"Successfully read Excel file with {len(df)} rows")
        print(f"Columns: {list(df.columns)}")
        
        # Check for the required columns
        required_columns = ['الرقم الوزاري', 'الاسم', 'الرقم المدني', 'الوظيفة', 'اسم القسم']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"Missing required columns: {missing_columns}")
        else:
            print("All required columns are present")
        
        # Print the first 3 rows
        print("\nFirst 3 rows:")
        for i, row in df.head(3).iterrows():
            print(f"Row {i+1}:")
            for col in df.columns:
                print(f"  {col}: {row[col]}")
        
        return True
    except Exception as e:
        print(f"Error reading Excel file: {str(e)}")
        return False

def main():
    # Create a test Excel file
    print("Creating test Excel file...")
    test_file_path = create_test_excel()
    print(f"Test file created at: {test_file_path}")
    
    # Check the test file
    check_excel_file(test_file_path)
    
    # Ask user if they want to check their own file
    user_file = input("\nEnter path to your Excel file to check (or press Enter to skip): ").strip()
    if user_file:
        check_excel_file(user_file)
    
    # Clean up
    os.unlink(test_file_path)
    print("\nTest file removed")

if __name__ == "__main__":
    main() 