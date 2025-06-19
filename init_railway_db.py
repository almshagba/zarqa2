#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت إعداد قاعدة البيانات الأولية لـ Railway
يجب تشغيل هذا السكريبت بعد النشر الأول على Railway
"""

import os
import sys
from flask import Flask
from database import db
from models import User, Employee, School, Department
from werkzeug.security import generate_password_hash

def create_app():
    """إنشاء تطبيق Flask للإعداد"""
    app = Flask(__name__)
    
    # تحديد بيئة الإنتاج
    app.config['FLASK_ENV'] = 'production'
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'temp_key_for_setup')
    
    # إعداد قاعدة البيانات
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        print("تحذير: لم يتم العثور على DATABASE_URL")
        sys.exit(1)
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    return app

def init_database():
    """إنشاء الجداول الأولية"""
    print("إنشاء جداول قاعدة البيانات...")
    db.create_all()
    print("تم إنشاء الجداول بنجاح!")

def create_admin_user():
    """إنشاء مستخدم إداري افتراضي"""
    print("إنشاء المستخدم الإداري...")
    
    # التحقق من وجود مستخدم إداري
    admin_user = User.query.filter_by(username='admin').first()
    if admin_user:
        print("المستخدم الإداري موجود بالفعل")
        return
    
    # إنشاء مستخدم إداري جديد
    admin_user = User(
        username='admin',
        password_hash=generate_password_hash('admin123'),  # يجب تغيير كلمة المرور
        is_admin=True,
        is_active=True,
        full_name='مدير النظام',
        email='admin@example.com'
    )
    
    db.session.add(admin_user)
    db.session.commit()
    print("تم إنشاء المستخدم الإداري بنجاح!")
    print("اسم المستخدم: admin")
    print("كلمة المرور: admin123")
    print("⚠️  يرجى تغيير كلمة المرور فور تسجيل الدخول!")

def create_sample_data():
    """إنشاء بيانات تجريبية أساسية"""
    print("إنشاء البيانات الأساسية...")
    
    # إنشاء مدرسة تجريبية إذا لم تكن موجودة
    if not School.query.first():
        sample_school = School(
            name='مدرسة تجريبية',
            region='المنطقة الأولى',
            type='أساسية',
            gender='مختلطة'
        )
        db.session.add(sample_school)
        db.session.commit()
        print("تم إنشاء مدرسة تجريبية")

def main():
    """الدالة الرئيسية"""
    print("=== إعداد قاعدة البيانات لـ Railway ===")
    print("تحقق من متغيرات البيئة...")
    
    # التحقق من متغيرات البيئة المطلوبة
    required_vars = ['DATABASE_URL', 'SECRET_KEY']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"خطأ: متغيرات البيئة المفقودة: {', '.join(missing_vars)}")
        sys.exit(1)
    
    # إنشاء التطبيق وإعداد قاعدة البيانات
    app = create_app()
    
    with app.app_context():
        try:
            init_database()
            create_admin_user()
            create_sample_data()
            print("\n✅ تم إعداد قاعدة البيانات بنجاح!")
            print("يمكنك الآن الوصول إلى التطبيق وتسجيل الدخول")
        except Exception as e:
            print(f"❌ خطأ في إعداد قاعدة البيانات: {e}")
            sys.exit(1)

if __name__ == '__main__':
    main()