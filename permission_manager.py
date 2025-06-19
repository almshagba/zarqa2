from models_new import db, Permission, Role, User
from datetime import datetime

class PermissionManager:
    """مدير الصلاحيات والأدوار"""
    
    @staticmethod
    def create_default_permissions():
        """إنشاء الصلاحيات الافتراضية"""
        default_permissions = [
            # صلاحيات الموظفين
            ('employees.view', 'عرض الموظفين', 'عرض قائمة الموظفين وتفاصيلهم', 'employees'),
            ('employees.create', 'إضافة موظف', 'إضافة موظف جديد', 'employees'),
            ('employees.edit', 'تعديل الموظفين', 'تعديل بيانات الموظفين', 'employees'),
            ('employees.delete', 'حذف الموظفين', 'حذف الموظفين', 'employees'),
            ('employees.export', 'تصدير الموظفين', 'تصدير بيانات الموظفين', 'employees'),
            
            # صلاحيات المدارس
            ('schools.view', 'عرض المدارس', 'عرض قائمة المدارس وتفاصيلها', 'schools'),
            ('schools.create', 'إضافة مدرسة', 'إضافة مدرسة جديدة', 'schools'),
            ('schools.edit', 'تعديل المدارس', 'تعديل بيانات المدارس', 'schools'),
            ('schools.delete', 'حذف المدارس', 'حذف المدارس', 'schools'),
            
            # صلاحيات الإجازات
            ('leaves.view', 'عرض الإجازات', 'عرض قائمة الإجازات', 'leaves'),
            ('leaves.create', 'إضافة إجازة', 'إضافة إجازة جديدة', 'leaves'),
            ('leaves.edit', 'تعديل الإجازات', 'تعديل الإجازات', 'leaves'),
            ('leaves.delete', 'حذف الإجازات', 'حذف الإجازات', 'leaves'),
            ('leaves.approve', 'اعتماد الإجازات', 'اعتماد أو رفض الإجازات', 'leaves'),
            
            # صلاحيات المغادرات
            ('departures.view', 'عرض المغادرات', 'عرض قائمة المغادرات', 'departures'),
            ('departures.create', 'إضافة مغادرة', 'إضافة مغادرة جديدة', 'departures'),
            ('departures.edit', 'تعديل المغادرات', 'تعديل المغادرات', 'departures'),
            ('departures.delete', 'حذف المغادرات', 'حذف المغادرات', 'departures'),
            ('departures.process_monthly', 'معالجة المغادرات الشهرية', 'معالجة المغادرات الشهرية', 'departures'),
            
            # صلاحيات التقارير
            ('reports.view', 'عرض التقارير', 'عرض التقارير المختلفة', 'reports'),
            ('reports.export', 'تصدير التقارير', 'تصدير التقارير بصيغ مختلفة', 'reports'),
            ('reports.advanced', 'التقارير المتقدمة', 'الوصول للتقارير المتقدمة', 'reports'),
            
            # صلاحيات إدارة المستخدمين
            ('users.view', 'عرض المستخدمين', 'عرض قائمة المستخدمين', 'users'),
            ('users.create', 'إضافة مستخدم', 'إضافة مستخدم جديد', 'users'),
            ('users.edit', 'تعديل المستخدمين', 'تعديل بيانات المستخدمين', 'users'),
            ('users.delete', 'حذف المستخدمين', 'حذف المستخدمين', 'users'),
            ('users.manage_roles', 'إدارة أدوار المستخدمين', 'تعيين وإزالة أدوار المستخدمين', 'users'),
            
            # صلاحيات النظام
            ('system.backup', 'نسخ احتياطي', 'إنشاء نسخة احتياطية من قاعدة البيانات', 'system'),
            ('system.settings', 'إعدادات النظام', 'تعديل إعدادات النظام', 'system'),
            ('system.logs', 'سجلات النظام', 'عرض سجلات النظام', 'system'),
            
            # صلاحيات النماذج
            ('forms.view', 'عرض النماذج', 'عرض النماذج المختلفة', 'forms'),
            ('forms.manage', 'إدارة النماذج', 'إنشاء وتعديل النماذج', 'forms'),
        ]
        
        for name, display_name, description, category in default_permissions:
            if not Permission.query.filter_by(name=name).first():
                permission = Permission(
                    name=name,
                    display_name=display_name,
                    description=description,
                    category=category
                )
                db.session.add(permission)
        
        db.session.commit()
        print("تم إنشاء الصلاحيات الافتراضية بنجاح")
    
    @staticmethod
    def create_default_roles():
        """إنشاء الأدوار الافتراضية"""
        # إنشاء دور المدير العام
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(
                name='admin',
                display_name='مدير عام',
                description='مدير عام للنظام - لديه جميع الصلاحيات',
                is_admin=True
            )
            db.session.add(admin_role)
        
        # إنشاء دور موظف إدخال البيانات
        data_entry_role = Role.query.filter_by(name='data_entry').first()
        if not data_entry_role:
            data_entry_role = Role(
                name='data_entry',
                display_name='موظف إدخال بيانات',
                description='موظف مسؤول عن إدخال وتعديل البيانات الأساسية'
            )
            # إضافة الصلاحيات المناسبة
            permissions = Permission.query.filter(
                Permission.name.in_([
                    'employees.view', 'employees.create', 'employees.edit',
                    'schools.view', 'schools.create', 'schools.edit',
                    'leaves.view', 'leaves.create', 'leaves.edit',
                    'departures.view', 'departures.create', 'departures.edit'
                ])
            ).all()
            data_entry_role.permissions.extend(permissions)
            db.session.add(data_entry_role)
        
        # إنشاء دور مشرف التقارير
        reports_supervisor_role = Role.query.filter_by(name='reports_supervisor').first()
        if not reports_supervisor_role:
            reports_supervisor_role = Role(
                name='reports_supervisor',
                display_name='مشرف التقارير',
                description='مشرف مسؤول عن التقارير والتصدير'
            )
            # إضافة الصلاحيات المناسبة
            permissions = Permission.query.filter(
                Permission.name.in_([
                    'employees.view', 'employees.export',
                    'schools.view',
                    'leaves.view', 'leaves.approve',
                    'departures.view', 'departures.process_monthly',
                    'reports.view', 'reports.export', 'reports.advanced'
                ])
            ).all()
            reports_supervisor_role.permissions.extend(permissions)
            db.session.add(reports_supervisor_role)
        
        # إنشاء دور مدير الموارد البشرية
        hr_manager_role = Role.query.filter_by(name='hr_manager').first()
        if not hr_manager_role:
            hr_manager_role = Role(
                name='hr_manager',
                display_name='مدير الموارد البشرية',
                description='مدير مسؤول عن إدارة الموظفين والإجازات'
            )
            # إضافة الصلاحيات المناسبة
            permissions = Permission.query.filter(
                Permission.name.in_([
                    'employees.view', 'employees.create', 'employees.edit', 'employees.delete', 'employees.export',
                    'leaves.view', 'leaves.create', 'leaves.edit', 'leaves.delete', 'leaves.approve',
                    'departures.view', 'departures.create', 'departures.edit', 'departures.delete',
                    'reports.view', 'reports.export',
                    'users.view'
                ])
            ).all()
            hr_manager_role.permissions.extend(permissions)
            db.session.add(hr_manager_role)
        
        db.session.commit()
        print("تم إنشاء الأدوار الافتراضية بنجاح")
    
    @staticmethod
    def migrate_existing_users():
        """ترحيل المستخدمين الحاليين إلى النظام الجديد"""
        # هذه الدالة ستحتاج لتخصيص حسب البيانات الحالية
        # يمكن تشغيلها مرة واحدة فقط عند الترحيل
        pass