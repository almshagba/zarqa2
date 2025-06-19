#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت لترحيل الصلاحيات من النظام القديم إلى النظام الجديد
يقوم بإضافة الأعمدة الجديدة وتحديث صلاحيات المستخدمين الحاليين
"""

import sqlite3
import os
from datetime import datetime

def backup_database(db_path):
    """إنشاء نسخة احتياطية من قاعدة البيانات"""
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    try:
        # نسخ الملف
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ تم إنشاء نسخة احتياطية: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ خطأ في إنشاء النسخة الاحتياطية: {e}")
        return None

def add_new_permission_columns(cursor):
    """إضافة أعمدة الصلاحيات الجديدة"""
    new_columns = [
        # صلاحيات الموظفين
        ('view_employees', 'BOOLEAN DEFAULT 0'),
        ('edit_employees', 'BOOLEAN DEFAULT 0'),
        
        # صلاحيات المدارس
        ('view_schools', 'BOOLEAN DEFAULT 0'),
        ('edit_schools', 'BOOLEAN DEFAULT 0'),
        
        # صلاحيات الإجازات
        ('view_leaves', 'BOOLEAN DEFAULT 0'),
        ('edit_leaves', 'BOOLEAN DEFAULT 0'),
        
        # صلاحيات المغادرات
        ('view_departures', 'BOOLEAN DEFAULT 0'),
        ('edit_departures', 'BOOLEAN DEFAULT 0'),
        
        # صلاحيات النقل
        ('view_transfers', 'BOOLEAN DEFAULT 0'),
        ('edit_transfers', 'BOOLEAN DEFAULT 0'),
        
        # صلاحيات التقارير
        ('view_reports', 'BOOLEAN DEFAULT 0'),
        ('edit_reports', 'BOOLEAN DEFAULT 0'),
        
        # صلاحيات التصدير
        ('view_exports', 'BOOLEAN DEFAULT 0'),
        ('edit_exports', 'BOOLEAN DEFAULT 0'),
        
        # صلاحيات المستخدمين
        ('view_users', 'BOOLEAN DEFAULT 0'),
        ('edit_users', 'BOOLEAN DEFAULT 0'),
        
        # صلاحيات النماذج
        ('view_forms', 'BOOLEAN DEFAULT 0'),
        ('edit_forms', 'BOOLEAN DEFAULT 0'),
        
        # صلاحيات النظام
        ('view_system', 'BOOLEAN DEFAULT 0'),
        ('edit_system', 'BOOLEAN DEFAULT 0'),
        
        # الصلاحيات الخاصة
        ('school_admin', 'BOOLEAN DEFAULT 0'),
        ('directorate_admin', 'BOOLEAN DEFAULT 0'),
    ]
    
    added_columns = []
    
    for column_name, column_type in new_columns:
        try:
            cursor.execute(f"ALTER TABLE user ADD COLUMN {column_name} {column_type}")
            added_columns.append(column_name)
            print(f"✅ تم إضافة العمود: {column_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"⚠️  العمود {column_name} موجود مسبقاً")
            else:
                print(f"❌ خطأ في إضافة العمود {column_name}: {e}")
    
    return added_columns

def migrate_existing_permissions(cursor):
    """ترحيل الصلاحيات الموجودة إلى النظام الجديد"""
    print("\n🔄 بدء ترحيل الصلاحيات الموجودة...")
    
    # الحصول على جميع المستخدمين
    cursor.execute("SELECT id, username, is_admin FROM user")
    users = cursor.fetchall()
    
    for user_id, username, is_admin in users:
        print(f"\n👤 ترحيل صلاحيات المستخدم: {username}")
        
        if is_admin:
            # إعطاء جميع الصلاحيات للمديرين
            update_query = """
            UPDATE user SET 
                view_employees = 1, edit_employees = 1,
                view_schools = 1, edit_schools = 1,
                view_leaves = 1, edit_leaves = 1,
                view_departures = 1, edit_departures = 1,
                view_transfers = 1, edit_transfers = 1,
                view_reports = 1, edit_reports = 1,
                view_exports = 1, edit_exports = 1,
                view_users = 1, edit_users = 1,
                view_forms = 1, edit_forms = 1,
                view_system = 1, edit_system = 1,
                school_admin = 1, directorate_admin = 1
            WHERE id = ?
            """
            cursor.execute(update_query, (user_id,))
            print(f"   ✅ تم إعطاء جميع الصلاحيات للمدير: {username}")
        else:
            # ترحيل الصلاحيات الموجودة للمستخدمين العاديين
            # الحصول على الصلاحيات الحالية
            cursor.execute("""
                SELECT can_manage_employees, can_manage_schools, can_manage_leaves,
                       can_manage_departures, can_manage_transfers, can_manage_reports,
                       can_manage_exports, can_manage_users, can_manage_forms
                FROM user WHERE id = ?
            """, (user_id,))
            
            current_perms = cursor.fetchone()
            if current_perms:
                # تحديث الصلاحيات الجديدة بناءً على الصلاحيات القديمة
                updates = []
                values = []
                
                # صلاحيات الموظفين
                if current_perms[0]:  # can_manage_employees
                    updates.extend(['view_employees = ?', 'edit_employees = ?'])
                    values.extend([1, 1])
                
                # صلاحيات المدارس
                if current_perms[1]:  # can_manage_schools
                    updates.extend(['view_schools = ?', 'edit_schools = ?'])
                    values.extend([1, 1])
                
                # صلاحيات الإجازات
                if current_perms[2]:  # can_manage_leaves
                    updates.extend(['view_leaves = ?', 'edit_leaves = ?'])
                    values.extend([1, 1])
                
                # صلاحيات المغادرات
                if current_perms[3]:  # can_manage_departures
                    updates.extend(['view_departures = ?', 'edit_departures = ?'])
                    values.extend([1, 1])
                
                # صلاحيات النقل
                if current_perms[4]:  # can_manage_transfers
                    updates.extend(['view_transfers = ?', 'edit_transfers = ?'])
                    values.extend([1, 1])
                
                # صلاحيات التقارير
                if current_perms[5]:  # can_manage_reports
                    updates.extend(['view_reports = ?', 'edit_reports = ?'])
                    values.extend([1, 1])
                
                # صلاحيات التصدير
                if current_perms[6]:  # can_manage_exports
                    updates.extend(['view_exports = ?', 'edit_exports = ?'])
                    values.extend([1, 1])
                
                # صلاحيات المستخدمين
                if current_perms[7]:  # can_manage_users
                    updates.extend(['view_users = ?', 'edit_users = ?'])
                    values.extend([1, 1])
                
                # صلاحيات النماذج
                if current_perms[8]:  # can_manage_forms
                    updates.extend(['view_forms = ?', 'edit_forms = ?'])
                    values.extend([1, 1])
                
                if updates:
                    values.append(user_id)
                    update_query = f"UPDATE user SET {', '.join(updates)} WHERE id = ?"
                    cursor.execute(update_query, values)
                    print(f"   ✅ تم ترحيل الصلاحيات للمستخدم: {username}")
                else:
                    print(f"   ⚠️  لا توجد صلاحيات للترحيل للمستخدم: {username}")

def verify_migration(cursor):
    """التحقق من نجاح عملية الترحيل"""
    print("\n🔍 التحقق من نجاح عملية الترحيل...")
    
    # عدد المستخدمين
    cursor.execute("SELECT COUNT(*) FROM user")
    total_users = cursor.fetchone()[0]
    
    # عدد المديرين
    cursor.execute("SELECT COUNT(*) FROM user WHERE is_admin = 1")
    admin_users = cursor.fetchone()[0]
    
    # عدد المستخدمين الذين لديهم صلاحيات
    cursor.execute("""
        SELECT COUNT(*) FROM user WHERE 
        view_employees = 1 OR edit_employees = 1 OR
        view_schools = 1 OR edit_schools = 1 OR
        view_leaves = 1 OR edit_leaves = 1
    """)
    users_with_perms = cursor.fetchone()[0]
    
    print(f"📊 إحصائيات الترحيل:")
    print(f"   - إجمالي المستخدمين: {total_users}")
    print(f"   - المديرين: {admin_users}")
    print(f"   - المستخدمين الذين لديهم صلاحيات: {users_with_perms}")
    
    # عرض تفاصيل المستخدمين
    cursor.execute("""
        SELECT username, is_admin, 
               view_employees, edit_employees,
               view_schools, edit_schools,
               view_leaves, edit_leaves
        FROM user
    """)
    
    users = cursor.fetchall()
    print("\n👥 تفاصيل المستخدمين:")
    for user in users:
        username, is_admin = user[0], user[1]
        perms = user[2:]
        active_perms = sum(perms)
        status = "مدير" if is_admin else f"{active_perms} صلاحية"
        print(f"   - {username}: {status}")

def main():
    """الدالة الرئيسية لتنفيذ عملية الترحيل"""
    print("🚀 بدء عملية ترحيل الصلاحيات إلى النظام الجديد")
    print("=" * 50)
    
    db_path = 'employees.db'
    
    # التحقق من وجود قاعدة البيانات
    if not os.path.exists(db_path):
        print(f"❌ لم يتم العثور على قاعدة البيانات: {db_path}")
        return
    
    # إنشاء نسخة احتياطية
    backup_path = backup_database(db_path)
    if not backup_path:
        print("❌ فشل في إنشاء النسخة الاحتياطية. توقف العملية.")
        return
    
    try:
        # الاتصال بقاعدة البيانات
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n📝 إضافة أعمدة الصلاحيات الجديدة...")
        added_columns = add_new_permission_columns(cursor)
        
        if added_columns:
            print(f"✅ تم إضافة {len(added_columns)} عمود جديد")
        
        # ترحيل الصلاحيات الموجودة
        migrate_existing_permissions(cursor)
        
        # حفظ التغييرات
        conn.commit()
        print("\n💾 تم حفظ جميع التغييرات")
        
        # التحقق من النتائج
        verify_migration(cursor)
        
        print("\n🎉 تمت عملية الترحيل بنجاح!")
        print(f"📁 النسخة الاحتياطية محفوظة في: {backup_path}")
        
    except Exception as e:
        print(f"❌ خطأ أثناء عملية الترحيل: {e}")
        print(f"🔄 يمكنك استعادة النسخة الاحتياطية من: {backup_path}")
    
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()