#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to migrate data from SQLite to PostgreSQL
يستخدم هذا السكريبت لنقل البيانات من SQLite إلى PostgreSQL
"""

import sqlite3
import psycopg2
import os
from datetime import datetime
import json

def connect_sqlite(db_path='employees.db'):
    """
    الاتصال بقاعدة بيانات SQLite
    """
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # للحصول على النتائج كـ dictionary
        return conn
    except Exception as e:
        print(f"خطأ في الاتصال بـ SQLite: {e}")
        return None

def connect_postgres():
    """
    الاتصال بقاعدة بيانات PostgreSQL
    """
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            # إعدادات افتراضية للتطوير
            database_url = "postgresql://postgres:postgres_password@localhost:5432/employees_db"
        
        conn = psycopg2.connect(database_url)
        return conn
    except Exception as e:
        print(f"خطأ في الاتصال بـ PostgreSQL: {e}")
        return None

def get_table_schema(sqlite_conn, table_name):
    """
    الحصول على schema الجدول من SQLite
    """
    cursor = sqlite_conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    return cursor.fetchall()

def get_all_tables(sqlite_conn):
    """
    الحصول على قائمة بجميع الجداول في SQLite
    """
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    return [row[0] for row in cursor.fetchall()]

def migrate_table_data(sqlite_conn, postgres_conn, table_name):
    """
    نقل بيانات جدول واحد من SQLite إلى PostgreSQL
    """
    try:
        # قراءة البيانات من SQLite
        sqlite_cursor = sqlite_conn.cursor()
        sqlite_cursor.execute(f"SELECT * FROM {table_name}")
        rows = sqlite_cursor.fetchall()
        
        if not rows:
            print(f"لا توجد بيانات في جدول {table_name}")
            return True
        
        # الحصول على أسماء الأعمدة
        column_names = [description[0] for description in sqlite_cursor.description]
        
        # إعداد استعلام الإدراج في PostgreSQL
        placeholders = ', '.join(['%s'] * len(column_names))
        columns = ', '.join(column_names)
        insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        
        # إدراج البيانات في PostgreSQL
        postgres_cursor = postgres_conn.cursor()
        
        for row in rows:
            try:
                # تحويل البيانات إذا لزم الأمر
                row_data = []
                for value in row:
                    if isinstance(value, str) and value.lower() in ['true', 'false']:
                        # تحويل النصوص البوليانية
                        row_data.append(value.lower() == 'true')
                    else:
                        row_data.append(value)
                
                postgres_cursor.execute(insert_query, row_data)
            except Exception as e:
                print(f"خطأ في إدراج صف في جدول {table_name}: {e}")
                print(f"البيانات: {row}")
                continue
        
        postgres_conn.commit()
        print(f"تم نقل {len(rows)} صف من جدول {table_name}")
        return True
        
    except Exception as e:
        print(f"خطأ في نقل جدول {table_name}: {e}")
        postgres_conn.rollback()
        return False

def create_postgres_tables():
    """
    إنشاء الجداول في PostgreSQL باستخدام Flask models
    """
    try:
        from app import app, db
        
        with app.app_context():
            # حذف الجداول الموجودة (احذر!)
            db.drop_all()
            # إنشاء جداول جديدة
            db.create_all()
            print("تم إنشاء الجداول في PostgreSQL")
            return True
    except Exception as e:
        print(f"خطأ في إنشاء الجداول: {e}")
        return False

def backup_sqlite_data(sqlite_path='employees.db'):
    """
    إنشاء نسخة احتياطية من بيانات SQLite
    """
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f"backup_sqlite_{timestamp}.db"
        
        import shutil
        shutil.copy2(sqlite_path, backup_path)
        print(f"تم إنشاء نسخة احتياطية: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"خطأ في إنشاء النسخة الاحتياطية: {e}")
        return None

def main():
    """
    الدالة الرئيسية للنقل
    """
    print("بدء عملية نقل البيانات من SQLite إلى PostgreSQL...")
    
    # إنشاء نسخة احتياطية
    print("إنشاء نسخة احتياطية من SQLite...")
    backup_path = backup_sqlite_data()
    if not backup_path:
        print("فشل في إنشاء النسخة الاحتياطية. توقف العملية.")
        return False
    
    # الاتصال بقواعد البيانات
    print("الاتصال بقواعد البيانات...")
    sqlite_conn = connect_sqlite()
    postgres_conn = connect_postgres()
    
    if not sqlite_conn or not postgres_conn:
        print("فشل في الاتصال بقواعد البيانات")
        return False
    
    try:
        # إنشاء الجداول في PostgreSQL
        print("إنشاء الجداول في PostgreSQL...")
        if not create_postgres_tables():
            return False
        
        # الحصول على قائمة الجداول
        tables = get_all_tables(sqlite_conn)
        print(f"الجداول الموجودة: {tables}")
        
        # نقل البيانات لكل جدول
        success_count = 0
        for table in tables:
            if table.startswith('sqlite_'):  # تجاهل جداول النظام
                continue
                
            print(f"نقل جدول {table}...")
            if migrate_table_data(sqlite_conn, postgres_conn, table):
                success_count += 1
            else:
                print(f"فشل في نقل جدول {table}")
        
        print(f"تم نقل {success_count} من {len([t for t in tables if not t.startswith('sqlite_')])} جدول بنجاح")
        
    except Exception as e:
        print(f"خطأ عام في عملية النقل: {e}")
        return False
    
    finally:
        # إغلاق الاتصالات
        if sqlite_conn:
            sqlite_conn.close()
        if postgres_conn:
            postgres_conn.close()
    
    print("انتهت عملية النقل")
    return True

if __name__ == '__main__':
    # تحديد متغيرات البيئة إذا لزم الأمر
    if not os.environ.get('DATABASE_URL'):
        print("تحذير: لم يتم تعيين DATABASE_URL، سيتم استخدام الإعدادات الافتراضية")
        print("يمكنك تعيين DATABASE_URL كالتالي:")
        print("export DATABASE_URL='postgresql://username:password@host:port/database'")
    
    success = main()
    if success:
        print("\n✅ تم نقل البيانات بنجاح!")
        print("يمكنك الآن تشغيل التطبيق مع PostgreSQL")
    else:
        print("\n❌ فشل في نقل البيانات")
        print("يرجى مراجعة الأخطاء أعلاه وإعادة المحاولة")