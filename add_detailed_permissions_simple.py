import sqlite3
import os

# Get the database path
db_path = os.path.join('instance', 'employees.db')

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# List of new columns to add
new_columns = [
    # صلاحيات الموظفين المفصلة
    'can_view_employees',
    'can_add_employees', 
    'can_edit_employees',
    'can_delete_employees',
    'can_view_employee_details',
    
    # صلاحيات الإجازات المفصلة
    'can_view_leaves',
    'can_add_leaves',
    'can_edit_leaves', 
    'can_delete_leaves',
    'can_approve_leaves',
    'can_manage_leave_balances',
    
    # صلاحيات المغادرات المفصلة
    'can_view_departures',
    'can_add_departures',
    'can_edit_departures',
    'can_delete_departures', 
    'can_convert_departures',
    
    # صلاحيات التقارير المفصلة
    'can_view_employee_reports',
    'can_view_school_reports',
    'can_view_leave_reports',
    'can_view_departure_reports',
    'can_view_comprehensive_reports',
    
    # صلاحيات التصدير المفصلة
    'can_export_employees',
    'can_export_leaves',
    'can_export_departures',
    'can_export_balances',
    'can_export_reports',
    
    # صلاحيات إدارية إضافية
    'can_view_system_logs',
    'can_manage_system_settings',
    'can_view_statistics',
    
    # صلاحيات خاصة بالمدارس
    'can_view_own_school_only',
    'can_manage_school_employees',
    'can_view_school_statistics'
]

try:
    # Check which columns already exist
    cursor.execute("PRAGMA table_info(user)")
    existing_columns = [row[1] for row in cursor.fetchall()]
    
    # Add new columns that don't exist
    for column in new_columns:
        if column not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE user ADD COLUMN {column} BOOLEAN DEFAULT 0")
                print(f"Added column: {column}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" not in str(e):
                    print(f"Error adding column {column}: {e}")
                else:
                    print(f"Column {column} already exists")
        else:
            print(f"Column {column} already exists")
    
    # Commit the changes
    conn.commit()
    print("\nAll detailed permission columns have been added successfully!")
    
except Exception as e:
    print(f"Error: {e}")
    conn.rollback()
    
finally:
    conn.close()