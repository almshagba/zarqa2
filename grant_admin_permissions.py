# -*- coding: utf-8 -*-
import sqlite3
import os

def grant_all_permissions_to_admin():
    """إعطاء جميع الصلاحيات للمستخدم الإداري"""
    db_path = 'instance/employees.db'
    
    if not os.path.exists(db_path):
        print(f"قاعدة البيانات غير موجودة: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 البحث عن المستخدمين الإداريين...")
        
        # البحث عن جميع المدراء
        cursor.execute("SELECT id, username FROM user WHERE is_admin = 1")
        admin_users = cursor.fetchall()
        
        if not admin_users:
            print("❌ لا يوجد مستخدمين إداريين في النظام")
            return False
        
        print(f"✅ تم العثور على {len(admin_users)} مستخدم إداري:")
        for admin_id, username in admin_users:
            print(f"   - {username} (ID: {admin_id})")
        
        # الحصول على جميع أعمدة الصلاحيات
        cursor.execute("PRAGMA table_info(user)")
        columns = cursor.fetchall()
        
        # استخراج أعمدة الصلاحيات (التي تبدأ بـ can_)
        permission_columns = [col[1] for col in columns if col[1].startswith('can_')]
        
        print(f"\n📋 تم العثور على {len(permission_columns)} صلاحية:")
        for perm in permission_columns:
            print(f"   - {perm}")
        
        if not permission_columns:
            print("❌ لا توجد أعمدة صلاحيات في قاعدة البيانات")
            return False
        
        # إنشاء استعلام التحديث
        updates = ', '.join([f"{perm} = 1" for perm in permission_columns])
        query = f"UPDATE user SET {updates} WHERE is_admin = 1"
        
        print(f"\n🔄 تحديث الصلاحيات للمستخدمين الإداريين...")
        cursor.execute(query)
        conn.commit()
        
        print(f"✅ تم تحديث {len(permission_columns)} صلاحية لـ {len(admin_users)} مستخدم إداري")
        
        # التحقق من النتيجة
        print("\n📊 حالة المستخدمين الإداريين بعد التحديث:")
        for admin_id, username in admin_users:
            cursor.execute(f"SELECT COUNT(*) FROM user WHERE id = ? AND {' AND '.join([f'{perm} = 1' for perm in permission_columns[:5]])}", (admin_id,))
            result = cursor.fetchone()[0]
            print(f"   - {username}: {'✅ جميع الصلاحيات مفعلة' if result > 0 else '❌ مشكلة في الصلاحيات'}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False

if __name__ == '__main__':
    print("🚀 بدء عملية إعطاء جميع الصلاحيات للمستخدمين الإداريين...")
    print("=" * 60)
    
    success = grant_all_permissions_to_admin()
    
    print("=" * 60)
    if success:
        print("🎉 تم بنجاح! جميع المستخدمين الإداريين لديهم الآن جميع الصلاحيات المتاحة")
        print("\n📝 ملاحظة: المستخدمين الإداريين (is_admin = True) لديهم صلاحيات كاملة تلقائياً")
        print("   حتى لو لم تكن الأعمدة محدثة في قاعدة البيانات")
    else:
        print("❌ فشل في إعطاء الصلاحيات")
    
    input("\nاضغط Enter للخروج...")