from app import app, db
from models import User
from werkzeug.security import generate_password_hash
import traceback

def create_hr_user():
    """Create an HR user with view-only permissions"""
    try:
        print("Starting HR user creation process...")
        with app.app_context():
            # Check if HR user already exists
            existing_user = User.query.filter_by(username='hr').first()
            if existing_user:
                print("HR user already exists. Updating permissions...")
                hr_user = existing_user
            else:
                print("Creating new HR user...")
                hr_user = User(
                    username='hr',
                    full_name='مسؤول الموارد البشرية',
                    is_admin=False
                )
                hr_user.set_password('hr123456')  # Set a default password
                db.session.add(hr_user)
            
            # Set view-only permissions
            # Basic permissions - only view permissions
            hr_user.can_view_employees_list = True
            hr_user.can_view_employee_details = True
            hr_user.can_view_schools_list = True
            hr_user.can_view_school_details = True
            hr_user.can_view_leaves_list = True
            hr_user.can_view_leave_details = True
            hr_user.can_view_departures_list = True
            hr_user.can_view_departure_details = True
            hr_user.can_view_transfers_list = True
            hr_user.can_view_transfer_details = True
            
            # Detailed permissions - only view permissions
            hr_user.can_view_employees = True
            hr_user.can_view_leaves = True
            hr_user.can_view_departures = True
            
            # Report permissions - allow viewing reports
            hr_user.can_view_reports = True
            hr_user.can_view_employee_reports = True
            hr_user.can_view_school_reports = True
            hr_user.can_view_leave_reports = True
            hr_user.can_view_departure_reports = True
            hr_user.can_view_comprehensive_reports = True
            hr_user.can_view_statistics = True
            
            # Disable all edit/add/delete permissions
            hr_user.can_edit_employees_data = False
            hr_user.can_add_new_employee = False
            hr_user.can_delete_employee = False
            hr_user.can_edit_schools_data = False
            hr_user.can_add_new_school = False
            hr_user.can_delete_school = False
            hr_user.can_edit_leaves_data = False
            hr_user.can_add_new_leave = False
            hr_user.can_delete_leave = False
            hr_user.can_edit_departures_data = False
            hr_user.can_add_new_departure = False
            hr_user.can_delete_departure = False
            hr_user.can_edit_transfers_data = False
            hr_user.can_add_new_transfer = False
            hr_user.can_delete_transfer = False
            
            # Disable management permissions
            hr_user.can_manage_employees = False
            hr_user.can_manage_schools = False
            hr_user.can_manage_leaves = False
            hr_user.can_manage_departures = False
            hr_user.can_manage_transfers = False
            hr_user.can_manage_users = False
            hr_user.can_manage_forms = False
            hr_user.can_manage_system_settings = False
            hr_user.can_backup_database = False
            hr_user.can_process_monthly_departures = False
            
            # Disable detailed edit/add/delete permissions
            hr_user.can_add_employees = False
            hr_user.can_edit_employees = False
            hr_user.can_delete_employees = False
            hr_user.can_add_leaves = False
            hr_user.can_edit_leaves = False
            hr_user.can_delete_leaves = False
            hr_user.can_approve_leaves = False
            hr_user.can_manage_leave_balances = False
            hr_user.can_add_departures = False
            hr_user.can_edit_departures = False
            hr_user.can_delete_departures = False
            hr_user.can_convert_departures = False
            
            print("Committing changes to database...")
            db.session.commit()
            print(f"HR user created/updated successfully with username: hr")
            print("Default password: hr123456 (if newly created)")
            print("Please change the password after first login.")
    except Exception as e:
        print(f"Error creating HR user: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    create_hr_user() 