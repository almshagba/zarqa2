from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from database import db

class User(db.Model):
    """نموذج المستخدم مع نظام الصلاحيات المحدث والمنظم"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # ==================== صلاحيات الموظفين ====================
    # مشاهدة
    can_view_employees_list = db.Column(db.Boolean, default=False)  # عرض قائمة الموظفين
    can_view_employee_details = db.Column(db.Boolean, default=False)  # عرض تفاصيل الموظف
    
    # تعديل
    can_edit_employees_data = db.Column(db.Boolean, default=False)  # تعديل بيانات الموظفين
    can_edit_employee_details = db.Column(db.Boolean, default=False)  # تعديل تفاصيل الموظف
    can_add_new_employee = db.Column(db.Boolean, default=False)  # إضافة موظف جديد
    can_delete_employee = db.Column(db.Boolean, default=False)  # حذف موظف
    
    # ==================== صلاحيات المدارس ====================
    # مشاهدة
    can_view_schools_list = db.Column(db.Boolean, default=False)  # عرض قائمة المدارس
    can_view_school_details = db.Column(db.Boolean, default=False)  # عرض تفاصيل المدرسة
    
    # تعديل
    can_edit_schools_data = db.Column(db.Boolean, default=False)  # تعديل بيانات المدارس
    can_edit_school_details = db.Column(db.Boolean, default=False)  # تعديل تفاصيل المدرسة
    can_add_new_school = db.Column(db.Boolean, default=False)  # إضافة مدرسة جديدة
    can_delete_school = db.Column(db.Boolean, default=False)  # حذف مدرسة
    
    # ==================== صلاحيات الإجازات ====================
    # مشاهدة
    can_view_leaves_list = db.Column(db.Boolean, default=False)  # عرض قائمة الإجازات
    can_view_leave_details = db.Column(db.Boolean, default=False)  # عرض تفاصيل الإجازة
    
    # تعديل
    can_edit_leaves_data = db.Column(db.Boolean, default=False)  # تعديل بيانات الإجازات
    can_edit_leave_details = db.Column(db.Boolean, default=False)  # تعديل تفاصيل الإجازة
    can_add_new_leave = db.Column(db.Boolean, default=False)  # إضافة إجازة جديدة
    can_delete_leave = db.Column(db.Boolean, default=False)  # حذف إجازة
    can_approve_leave_requests = db.Column(db.Boolean, default=False)  # الموافقة على طلبات الإجازة
    can_manage_leave_balances = db.Column(db.Boolean, default=False)  # إدارة أرصدة الإجازات
    
    # ==================== صلاحيات المغادرات ====================
    # مشاهدة
    can_view_departures_list = db.Column(db.Boolean, default=False)  # عرض قائمة المغادرات
    can_view_departure_details = db.Column(db.Boolean, default=False)  # عرض تفاصيل المغادرة
    
    # تعديل
    can_edit_departures_data = db.Column(db.Boolean, default=False)  # تعديل بيانات المغادرات
    can_edit_departure_details = db.Column(db.Boolean, default=False)  # تعديل تفاصيل المغادرة
    can_add_new_departure = db.Column(db.Boolean, default=False)  # إضافة مغادرة جديدة
    can_delete_departure = db.Column(db.Boolean, default=False)  # حذف مغادرة
    can_convert_departures_to_leaves = db.Column(db.Boolean, default=False)  # تحويل المغادرات إلى إجازات
    can_process_monthly_departures = db.Column(db.Boolean, default=False)  # معالجة المغادرات الشهرية
    
    # ==================== صلاحيات النقل ====================
    # مشاهدة
    can_view_transfers_list = db.Column(db.Boolean, default=False)  # عرض قائمة النقل
    can_view_transfer_details = db.Column(db.Boolean, default=False)  # عرض تفاصيل النقل
    
    # تعديل
    can_edit_transfers_data = db.Column(db.Boolean, default=False)  # تعديل بيانات النقل
    can_edit_transfer_details = db.Column(db.Boolean, default=False)  # تعديل تفاصيل النقل
    can_add_new_transfer = db.Column(db.Boolean, default=False)  # إضافة نقل جديد
    can_delete_transfer = db.Column(db.Boolean, default=False)  # حذف نقل
    
    # ==================== صلاحيات التقارير ====================
    can_view_employee_reports = db.Column(db.Boolean, default=False)  # تقارير الموظفين
    can_view_school_reports = db.Column(db.Boolean, default=False)  # تقارير المدارس
    can_view_leave_reports = db.Column(db.Boolean, default=False)  # تقارير الإجازات
    can_view_departure_reports = db.Column(db.Boolean, default=False)  # تقارير المغادرات
    can_view_transfer_reports = db.Column(db.Boolean, default=False)  # تقارير النقل
    can_view_comprehensive_reports = db.Column(db.Boolean, default=False)  # التقارير الشاملة
    can_view_statistical_reports = db.Column(db.Boolean, default=False)  # التقارير الإحصائية
    
    # ==================== صلاحيات التصدير ====================
    can_export_employee_data = db.Column(db.Boolean, default=False)  # تصدير بيانات الموظفين
    can_export_school_data = db.Column(db.Boolean, default=False)  # تصدير بيانات المدارس
    can_export_leave_data = db.Column(db.Boolean, default=False)  # تصدير بيانات الإجازات
    can_export_departure_data = db.Column(db.Boolean, default=False)  # تصدير بيانات المغادرات
    can_export_transfer_data = db.Column(db.Boolean, default=False)  # تصدير بيانات النقل
    can_export_report_data = db.Column(db.Boolean, default=False)  # تصدير التقارير
    can_export_balance_data = db.Column(db.Boolean, default=False)  # تصدير بيانات الأرصدة
    
    # ==================== صلاحيات إدارة المستخدمين ====================
    # مشاهدة
    can_view_users_list = db.Column(db.Boolean, default=False)  # عرض قائمة المستخدمين
    can_view_user_details = db.Column(db.Boolean, default=False)  # عرض تفاصيل المستخدم
    
    # تعديل
    can_edit_users_data = db.Column(db.Boolean, default=False)  # تعديل بيانات المستخدمين
    can_edit_user_details = db.Column(db.Boolean, default=False)  # تعديل تفاصيل المستخدم
    can_add_new_user = db.Column(db.Boolean, default=False)  # إضافة مستخدم جديد
    can_delete_user = db.Column(db.Boolean, default=False)  # حذف مستخدم
    can_manage_user_permissions = db.Column(db.Boolean, default=False)  # إدارة صلاحيات المستخدمين
    
    # ==================== صلاحيات النماذج ====================
    # مشاهدة
    can_view_forms_list = db.Column(db.Boolean, default=False)  # عرض قائمة النماذج
    
    # تعديل
    can_edit_forms_data = db.Column(db.Boolean, default=False)  # تعديل النماذج
    can_add_new_form = db.Column(db.Boolean, default=False)  # إضافة نموذج جديد
    can_delete_form = db.Column(db.Boolean, default=False)  # حذف نموذج
    
    # ==================== صلاحيات النظام ====================
    can_view_system_logs = db.Column(db.Boolean, default=False)  # عرض سجلات النظام
    can_view_system_statistics = db.Column(db.Boolean, default=False)  # عرض إحصائيات النظام
    can_manage_system_settings = db.Column(db.Boolean, default=False)  # إدارة إعدادات النظام
    can_backup_database = db.Column(db.Boolean, default=False)  # نسخ احتياطي للقاعدة
    can_restore_database = db.Column(db.Boolean, default=False)  # استعادة قاعدة البيانات
    
    # ==================== صلاحيات خاصة ====================
    can_view_own_school_data_only = db.Column(db.Boolean, default=False)  # عرض بيانات المدرسة الخاصة فقط
    can_manage_own_school_employees = db.Column(db.Boolean, default=False)  # إدارة موظفي المدرسة الخاصة
    can_view_directorate_data = db.Column(db.Boolean, default=False)  # عرض بيانات المديرية
    can_manage_directorate_employees = db.Column(db.Boolean, default=False)  # إدارة موظفي المديرية
    
    def set_password(self, password):
        """تعيين كلمة المرور مع التشفير"""
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """فحص كلمة المرور"""
        return check_password_hash(self.password_hash, password)
    
    def has_permission(self, permission):
        """فحص ما إذا كان المستخدم لديه صلاحية معينة"""
        if self.is_admin:
            return True
            
        return getattr(self, permission, False)
    
    def get_permissions_by_category(self):
        """الحصول على الصلاحيات مجمعة حسب الفئة"""
        categories = {
            'employees': {
                'name': 'الموظفين',
                'view_permissions': [
                    ('can_view_employees_list', 'عرض قائمة الموظفين'),
                    ('can_view_employee_details', 'عرض تفاصيل الموظف')
                ],
                'edit_permissions': [
                    ('can_edit_employees_data', 'تعديل بيانات الموظفين'),
                    ('can_edit_employee_details', 'تعديل تفاصيل الموظف'),
                    ('can_add_new_employee', 'إضافة موظف جديد'),
                    ('can_delete_employee', 'حذف موظف')
                ]
            },
            'schools': {
                'name': 'المدارس',
                'view_permissions': [
                    ('can_view_schools_list', 'عرض قائمة المدارس'),
                    ('can_view_school_details', 'عرض تفاصيل المدرسة')
                ],
                'edit_permissions': [
                    ('can_edit_schools_data', 'تعديل بيانات المدارس'),
                    ('can_edit_school_details', 'تعديل تفاصيل المدرسة'),
                    ('can_add_new_school', 'إضافة مدرسة جديدة'),
                    ('can_delete_school', 'حذف مدرسة')
                ]
            },
            'leaves': {
                'name': 'الإجازات',
                'view_permissions': [
                    ('can_view_leaves_list', 'عرض قائمة الإجازات'),
                    ('can_view_leave_details', 'عرض تفاصيل الإجازة')
                ],
                'edit_permissions': [
                    ('can_edit_leaves_data', 'تعديل بيانات الإجازات'),
                    ('can_edit_leave_details', 'تعديل تفاصيل الإجازة'),
                    ('can_add_new_leave', 'إضافة إجازة جديدة'),
                    ('can_delete_leave', 'حذف إجازة'),
                    ('can_approve_leave_requests', 'الموافقة على طلبات الإجازة'),
                    ('can_manage_leave_balances', 'إدارة أرصدة الإجازات')
                ]
            },
            'departures': {
                'name': 'المغادرات',
                'view_permissions': [
                    ('can_view_departures_list', 'عرض قائمة المغادرات'),
                    ('can_view_departure_details', 'عرض تفاصيل المغادرة')
                ],
                'edit_permissions': [
                    ('can_edit_departures_data', 'تعديل بيانات المغادرات'),
                    ('can_edit_departure_details', 'تعديل تفاصيل المغادرة'),
                    ('can_add_new_departure', 'إضافة مغادرة جديدة'),
                    ('can_delete_departure', 'حذف مغادرة'),
                    ('can_convert_departures_to_leaves', 'تحويل المغادرات إلى إجازات'),
                    ('can_process_monthly_departures', 'معالجة المغادرات الشهرية')
                ]
            },
            'transfers': {
                'name': 'النقل',
                'view_permissions': [
                    ('can_view_transfers_list', 'عرض قائمة النقل'),
                    ('can_view_transfer_details', 'عرض تفاصيل النقل')
                ],
                'edit_permissions': [
                    ('can_edit_transfers_data', 'تعديل بيانات النقل'),
                    ('can_edit_transfer_details', 'تعديل تفاصيل النقل'),
                    ('can_add_new_transfer', 'إضافة نقل جديد'),
                    ('can_delete_transfer', 'حذف نقل')
                ]
            },
            'reports': {
                'name': 'التقارير',
                'view_permissions': [
                    ('can_view_employee_reports', 'تقارير الموظفين'),
                    ('can_view_school_reports', 'تقارير المدارس'),
                    ('can_view_leave_reports', 'تقارير الإجازات'),
                    ('can_view_departure_reports', 'تقارير المغادرات'),
                    ('can_view_transfer_reports', 'تقارير النقل'),
                    ('can_view_comprehensive_reports', 'التقارير الشاملة'),
                    ('can_view_statistical_reports', 'التقارير الإحصائية')
                ],
                'edit_permissions': []
            },
            'export': {
                'name': 'التصدير',
                'view_permissions': [],
                'edit_permissions': [
                    ('can_export_employee_data', 'تصدير بيانات الموظفين'),
                    ('can_export_school_data', 'تصدير بيانات المدارس'),
                    ('can_export_leave_data', 'تصدير بيانات الإجازات'),
                    ('can_export_departure_data', 'تصدير بيانات المغادرات'),
                    ('can_export_transfer_data', 'تصدير بيانات النقل'),
                    ('can_export_report_data', 'تصدير التقارير'),
                    ('can_export_balance_data', 'تصدير بيانات الأرصدة')
                ]
            },
            'users': {
                'name': 'المستخدمين',
                'view_permissions': [
                    ('can_view_users_list', 'عرض قائمة المستخدمين'),
                    ('can_view_user_details', 'عرض تفاصيل المستخدم')
                ],
                'edit_permissions': [
                    ('can_edit_users_data', 'تعديل بيانات المستخدمين'),
                    ('can_edit_user_details', 'تعديل تفاصيل المستخدم'),
                    ('can_add_new_user', 'إضافة مستخدم جديد'),
                    ('can_delete_user', 'حذف مستخدم'),
                    ('can_manage_user_permissions', 'إدارة صلاحيات المستخدمين')
                ]
            },
            'forms': {
                'name': 'النماذج',
                'view_permissions': [
                    ('can_view_forms_list', 'عرض قائمة النماذج')
                ],
                'edit_permissions': [
                    ('can_edit_forms_data', 'تعديل النماذج'),
                    ('can_add_new_form', 'إضافة نموذج جديد'),
                    ('can_delete_form', 'حذف نموذج')
                ]
            },
            'system': {
                'name': 'النظام',
                'view_permissions': [
                    ('can_view_system_logs', 'عرض سجلات النظام'),
                    ('can_view_system_statistics', 'عرض إحصائيات النظام')
                ],
                'edit_permissions': [
                    ('can_manage_system_settings', 'إدارة إعدادات النظام'),
                    ('can_backup_database', 'نسخ احتياطي للقاعدة'),
                    ('can_restore_database', 'استعادة قاعدة البيانات')
                ]
            },
            'special': {
                'name': 'صلاحيات خاصة',
                'view_permissions': [
                    ('can_view_own_school_data_only', 'عرض بيانات المدرسة الخاصة فقط'),
                    ('can_view_directorate_data', 'عرض بيانات المديرية')
                ],
                'edit_permissions': [
                    ('can_manage_own_school_employees', 'إدارة موظفي المدرسة الخاصة'),
                    ('can_manage_directorate_employees', 'إدارة موظفي المديرية')
                ]
            }
        }
        
        return categories
    
    def __repr__(self):
        return f'<User {self.username}>'