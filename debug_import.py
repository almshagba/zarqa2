from flask import Flask, session
import pandas as pd
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

def debug_import_function():
    print("Testing import functionality...")
    
    try:
        with app.app_context():
            # Test the school lookup functionality
            print("Testing school lookup...")
            all_schools = School.query.all()
            school_names = {school.name.strip(): school for school in all_schools}
            print(f"Found {len(school_names)} schools")
            
            # Test the similar schools dictionary creation
            print("Testing similar schools dictionary...")
            similar_schools = {}
            for name in school_names:
                clean_name = name.replace('ال', '').replace(' ', '').strip()
                similar_schools[clean_name] = school_names[name]
            print(f"Created {len(similar_schools)} similar school entries")
            
            # Test directorate departments
            print("Testing directorate departments...")
            print(f"DIRECTORATE_DEPARTMENTS: {DIRECTORATE_DEPARTMENTS}")
            directorate_dept_clean = [dept.replace('ال', '').replace(' ', '').strip() for dept in DIRECTORATE_DEPARTMENTS]
            print(f"Cleaned directorate departments: {directorate_dept_clean}")
            
            # Test date parsing
            print("Testing date parsing...")
            from routes.main_routes import parse_date_flexible
            test_dates = ['2023-01-15', '15/01/2023', '15-01-2023', '2023/01/15', '١٥/٠١/٢٠٢٣']
            for date_str in test_dates:
                try:
                    parsed_date = parse_date_flexible(date_str)
                    print(f"Parsed {date_str} as {parsed_date}")
                except Exception as e:
                    print(f"Error parsing {date_str}: {str(e)}")
    
    except Exception as e:
        print(f"Error during import testing: {str(e)}")

if __name__ == '__main__':
    debug_import_function() 