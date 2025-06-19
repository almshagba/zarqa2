#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Initialization Script for Render Deployment
This script initializes the database with tables and sample data
"""

import os
import sys
import logging
from datetime import datetime, date
from werkzeug.security import generate_password_hash

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app, db
    from models import User, Employee, LeaveRequest, School
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    sys.exit(1)

def format_database_url(url):
    """Format database URL for PostgreSQL compatibility"""
    if url and url.startswith('postgres://'):
        return url.replace('postgres://', 'postgresql://', 1)
    return url

def check_environment():
    """Check if running on Render"""
    is_render = os.environ.get('RENDER') == 'true'
    database_url = os.environ.get('DATABASE_URL')
    
    logger.info(f"Environment: {'Render' if is_render else 'Local'}")
    logger.info(f"Database URL configured: {'Yes' if database_url else 'No'}")
    
    return is_render, database_url

def create_tables():
    """Create all database tables"""
    try:
        with app.app_context():
            logger.info("Creating database tables...")
            db.create_all()
            logger.info("✓ Database tables created successfully")
            return True
    except Exception as e:
        logger.error(f"✗ Error creating tables: {e}")
        return False

def create_admin_user():
    """Create default admin user"""
    try:
        with app.app_context():
            # Check if admin user exists
            admin = User.query.filter_by(username='admin').first()
            if admin:
                logger.info("✓ Admin user already exists")
                return True
            
            # Create new admin user
            admin_user = User(
                username='admin',
                email='admin@company.com',
                password_hash=generate_password_hash('admin123'),
                role='admin',
                is_active=True
            )
            
            db.session.add(admin_user)
            db.session.commit()
            logger.info("✓ Admin user created successfully")
            logger.info("   Username: admin")
            logger.info("   Password: admin123")
            return True
            
    except Exception as e:
        logger.error(f"✗ Error creating admin user: {e}")
        db.session.rollback()
        return False

def create_sample_data():
    """Create sample data"""
    try:
        with app.app_context():
            # Create sample school
            school = School.query.first()
            if not school:
                school = School(
                    name='Model High School',
                    address='Riyadh, Saudi Arabia',
                    phone='011-1234567',
                    email='info@model-school.edu.sa'
                )
                db.session.add(school)
                db.session.flush()  # Get the ID
            
            # Create sample employee
            employee = Employee.query.first()
            if not employee:
                employee = Employee(
                    name='Ahmed Mohammed Ali',
                    employee_id='EMP001',
                    email='ahmed@model-school.edu.sa',
                    phone='0501234567',
                    position='Math Teacher',
                    school_id=school.id,
                    hire_date=date.today(),
                    salary=8000.00,
                    is_active=True
                )
                db.session.add(employee)
            
            db.session.commit()
            logger.info("✓ Sample data created successfully")
            return True
            
    except Exception as e:
        logger.error(f"✗ Error creating sample data: {e}")
        db.session.rollback()
        return False

def main():
    """Main function"""
    logger.info("🚀 Starting database setup for Render...")
    logger.info(f"📅 Start time: {datetime.now()}")
    
    # Check environment
    is_render, database_url = check_environment()
    
    if not database_url:
        logger.warning("⚠️ Warning: DATABASE_URL not found")
        logger.warning("   Make sure PostgreSQL service is configured in Render")
        return False
    
    # Execute setup steps
    steps = [
        ("Creating tables", create_tables),
        ("Creating admin user", create_admin_user),
        ("Creating sample data", create_sample_data)
    ]
    
    success_count = 0
    for step_name, step_func in steps:
        logger.info(f"\n📋 {step_name}...")
        if step_func():
            success_count += 1
        else:
            logger.error(f"❌ Failed: {step_name}")
    
    logger.info(f"\n📊 Results: {success_count}/{len(steps)} steps succeeded")
    
    if success_count == len(steps):
        logger.info("🎉 Database setup completed successfully!")
        logger.info("\n📝 Login information:")
        logger.info("   URL: https://your-app-name.onrender.com")
        logger.info("   Username: admin")
        logger.info("   Password: admin123")
        logger.info("\n⚠️ Remember to change admin password after first login!")
        return True
    else:
        logger.error("❌ Database setup failed")
        logger.error("   Check the logs above for errors")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)