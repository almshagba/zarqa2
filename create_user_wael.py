#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to create user 'wael' with full permissions
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash

def create_user_wael():
    """Create user 'wael' with full permissions"""
    db_path = 'instance/employees.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Checking for existing user 'wael'...")
        
        # Check if user 'wael' already exists
        cursor.execute("SELECT id, username FROM user WHERE username = 'wael'")
        existing_user = cursor.fetchone()
        
        if existing_user:
            print(f"⚠️ User 'wael' already exists with ID: {existing_user[0]}")
            user_id = existing_user[0]
            print("Updating existing user...")
        else:
            print("Creating new user 'wael'...")
            
            # Generate password hash for '123456'
            password_hash = generate_password_hash('123456')
            
            # Create new user
            cursor.execute("""
                INSERT INTO user (username, password_hash, full_name, is_admin, created_at)
                VALUES ('wael', ?, 'Wael User', 1, datetime('now'))
            """, (password_hash,))
            
            user_id = cursor.lastrowid
            print(f"✅ Created user 'wael' with ID: {user_id}")
        
        # Get table columns
        cursor.execute("PRAGMA table_info(user)")
        columns_info = cursor.fetchall()
        all_columns = [col[1] for col in columns_info]
        
        print(f"📋 Total columns in table: {len(all_columns)}")
        
        # Comprehensive list of all permissions
        all_permissions = [
            'can_backup_database',
            'can_view_employees_list', 'can_view_employee_details', 'can_edit_employees_data',
            'can_add_new_employee', 'can_delete_employee',
            'can_view_schools_list', 'can_view_school_details', 'can_edit_schools_data',
            'can_add_new_school', 'can_delete_school',
            'can_view_leaves_list', 'can_view_leave_details', 'can_edit_leaves_data',
            'can_add_new_leave', 'can_delete_leave', 'can_manage_leave_balances',
            'can_view_departures_list', 'can_view_departure_details', 'can_edit_departures_data',
            'can_add_new_departure', 'can_delete_departure',
            'can_view_transfers_list', 'can_view_transfer_details', 'can_edit_transfers_data',
            'can_add_new_transfer', 'can_delete_transfer',
            'can_view_employee_reports', 'can_view_school_reports', 'can_view_comprehensive_reports',
            'can_export_employee_data', 'can_export_school_data', 'can_export_report_data',
            'can_view_users_list', 'can_add_new_user', 'can_manage_user_permissions',
            'can_view_forms_list', 'can_edit_forms_data', 'can_add_new_form', 'can_delete_form',
            'can_view_system_logs', 'can_manage_system_settings', 'can_process_monthly_departures',
            'can_view_employees', 'can_add_employees', 'can_edit_employees', 'can_delete_employees',
            'can_view_leaves', 'can_add_leaves', 'can_edit_leaves', 'can_delete_leaves',
            'can_approve_leaves', 'can_view_departures', 'can_add_departures',
            'can_edit_departures', 'can_delete_departures', 'can_convert_departures',
            'can_view_leave_reports', 'can_view_departure_reports',
            'can_export_employees', 'can_export_leaves', 'can_export_departures',
            'can_export_balances', 'can_export_reports', 'can_view_statistics',
            'can_view_own_school_only', 'can_manage_school_assignments'
        ]
        
        # Filter existing permissions
        existing_permissions = [p for p in all_permissions if p in all_columns]
        missing_permissions = [p for p in all_permissions if p not in all_columns]
        
        print(f"✅ Existing permissions: {len(existing_permissions)}")
        if missing_permissions:
            print(f"⚠️ Missing permissions: {len(missing_permissions)}")
            for perm in missing_permissions[:5]:  # Show first 5 only
                print(f"   - {perm}")
            if len(missing_permissions) > 5:
                print(f"   ... and {len(missing_permissions) - 5} more")
        
        if existing_permissions:
            # Update existing permissions
            updates = ', '.join([f"{perm} = 1" for perm in existing_permissions])
            query = f"UPDATE user SET is_admin = 1, {updates} WHERE username = 'wael'"
            cursor.execute(query)
            print(f"✅ Updated {len(existing_permissions)} permissions for user 'wael'")
        else:
            print("❌ No permission columns found in database")
            # At least set as admin
            cursor.execute("UPDATE user SET is_admin = 1 WHERE username = 'wael'")
            print("✅ Set user 'wael' as admin")
        
        # Save changes
        conn.commit()
        
        # Verify result
        cursor.execute("SELECT username, is_admin FROM user WHERE username = 'wael'")
        result = cursor.fetchone()
        
        if result:
            username, is_admin = result
            print(f"\n🎉 Final Result:")
            print(f"   Username: {username}")
            print(f"   Admin: {'Yes' if is_admin else 'No'}")
            print(f"   Updated permissions: {len(existing_permissions)}")
            print(f"   Password: 123456")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Starting creation of user 'wael' with full permissions...")
    print("=" * 60)
    
    success = create_user_wael()
    
    print("=" * 60)
    if success:
        print("✅ Success! User 'wael' now has full permissions")
        print("Login credentials:")
        print("   Username: wael")
        print("   Password: 123456")
    else:
        print("❌ Failed to create/update user")
        print("Please check the errors above")
    
    print("\nPress Enter to exit...")
    input()