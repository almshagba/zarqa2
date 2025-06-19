from database import db
from models_new import Permission, Role, User
from permission_manager import PermissionManager
from sqlalchemy import text

def migrate_to_rbac_system():
    """ترحيل النظام الحالي إلى نظام RBAC الجديد"""
    
    print("🚀 بدء ترحيل النظام إلى نظام الأدوار والصلاحيات الجديد...")
    
    try:
        # 1. إنشاء الجداول الجديدة
        print("📋 إنشاء الجداول الجديدة...")
        db.create_all()
        
        # 2. إنشاء الصلاحيات الافتراضية
        print("🔑 إنشاء الصلاحيات الافتراضية...")
        PermissionManager.create_default_permissions()
        
        # 3. إنشاء الأدوار الافتراضية
        print("👥 إنشاء الأدوار الافتراضية...")
        PermissionManager.create_default_roles()
        
        # 4. ترحيل المستخدمين الحاليين
        print("👤 ترحيل المستخدمين الحاليين...")
        migrate_existing_users()
        
        print("✅ تم الترحيل بنجاح!")
        
    except Exception as e:
        print(f"❌ خطأ في الترحيل: {e}")
        db.session.rollback()
        raise

def migrate_existing_users():
    """ترحيل المستخدمين من النظام القديم"""
    
    # الحصول على المستخدمين من الجدول القديم
    old_users_query = text("""
        SELECT id, username, password_hash, full_name, is_admin,
               can_manage_employees, can_manage_schools, can_manage_leaves,
               can_manage_departures, can_view_reports, can_export_data,
               can_manage_users, can_manage_forms, can_process_monthly_departures
        FROM users
    """)
    
    old_users = db.session.execute(old_users_query).fetchall()
    
    # الحصول على الأدوار
    admin_role = Role.query.filter_by(name='admin').first()
    data_entry_role = Role.query.filter_by(name='data_entry').first()
    reports_supervisor_role = Role.query.filter_by(name='reports_supervisor').first()
    hr_manager_role = Role.query.filter_by(name='hr_manager').first()
    
    for old_user in old_users:
        # إنشاء المستخدم الجديد
        new_user = User(
            username=old_user.username,
            password_hash=old_user.password_hash,
            full_name=old_user.full_name,
            is_active=True
        )
        
        # تحديد الأدوار بناءً على الصلاحيات القديمة
        if old_user.is_admin:
            new_user.roles.append(admin_role)
        else:
            # تحديد الأدوار بناءً على الصلاحيات
            if old_user.can_manage_employees and old_user.can_manage_leaves:
                new_user.roles.append(hr_manager_role)
            elif old_user.can_view_reports and old_user.can_export_data:
                new_user.roles.append(reports_supervisor_role)
            elif (old_user.can_manage_employees or old_user.can_manage_schools or 
                  old_user.can_manage_leaves or old_user.can_manage_departures):
                new_user.roles.append(data_entry_role)
        
        db.session.add(new_user)
    
    db.session.commit()
    print(f"تم ترحيل {len(old_users)} مستخدم بنجاح")

if __name__ == '__main__':
    migrate_to_rbac_system()