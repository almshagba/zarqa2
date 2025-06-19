from database import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ministry_number = db.Column(db.String(20), unique=True, nullable=False)  # الرقم الوزاري
    name = db.Column(db.String(100), nullable=False)  # الاسم
    civil_id = db.Column(db.String(20), unique=True, nullable=False)  # الرقم المدني (changed from national_id)
    gender = db.Column(db.String(10), nullable=False)  # الجنس
    job_title = db.Column(db.String(50), nullable=False)  # الوظيفة
    qualification = db.Column(db.String(50), nullable=False)  # المؤهل
    bachelor_specialization = db.Column(db.String(100))  # تخصص بكالوريوس
    high_diploma_specialization = db.Column(db.String(100))  # تخصص دبلوم العالي
    masters_specialization = db.Column(db.String(100))  # تخصص ماجستير
    phd_specialization = db.Column(db.String(100))  # تخصص دكتوراه
    subject = db.Column(db.String(100))  # المبحث الدراسي
    phone_number = db.Column(db.String(20))  # رقم الهاتف
    appointment_date = db.Column(db.Date, nullable=False)  # تاريخ التعيين
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)  # المدرسة
    is_directorate_employee = db.Column(db.Boolean, default=False)  # موظف مديرية
    
    # العلاقة مع المدرسة
    school = db.relationship('School', backref=db.backref('employees', lazy=True))
    
    # سجل النقل
    transfers = db.relationship('Transfer', backref='employee', lazy=True, cascade="all, delete-orphan")
    
    # سجل الإجازات
    leaves = db.relationship('Leave', backref='employee', lazy=True, cascade="all, delete-orphan")
    
    # إضافة العلاقة مع أرصدة الإجازات مع cascade
    leave_balances = db.relationship('LeaveBalance', backref='employee', lazy=True, cascade="all, delete-orphan")
    
    # إضافة العلاقة مع المغادرات المحولة مع cascade
    converted_departures = db.relationship('ConvertedDeparture', backref='employee', lazy=True, cascade="all, delete-orphan")
    
    # إضافة العلاقة مع أرصدة المغادرات الشهرية مع cascade
    monthly_departure_balances = db.relationship('MonthlyDepartureBalance', backref='employee', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Employee {self.name}>'

class School(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # اسم المدرسة
    phone = db.Column(db.String(20))  # رقم هاتف المدرسة
    address = db.Column(db.String(200))  # عنوان المدرسة
    gender = db.Column(db.String(20))  # جنس المدرسة (ذكور، إناث، مختلطة)
    region = db.Column(db.String(50))  # المنطقة
    
    def __repr__(self):
        return f'<School {self.name}>'

class Transfer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)  # الموظف
    from_school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)  # من مدرسة
    to_school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)  # إلى مدرسة
    from_job = db.Column(db.String(50))  # من وظيفة
    to_job = db.Column(db.String(50))  # إلى وظيفة
    transfer_date = db.Column(db.Date, default=datetime.utcnow)  # تاريخ النقل
    reason = db.Column(db.Text)  # سبب النقل
    
    # العلاقات - تحديث العلاقات مع المدارس
    from_school = db.relationship('School', foreign_keys=[from_school_id], backref=db.backref('transfers_from', lazy=True))
    to_school = db.relationship('School', foreign_keys=[to_school_id], backref=db.backref('transfers_to', lazy=True))
    
    def __repr__(self):
        return f'<Transfer {self.employee_id} from {self.from_school_id} to {self.to_school_id}>'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    can_backup_database = db.Column(db.Boolean, default=False)
    
    # Employee permissions
    can_view_employees_list = db.Column(db.Boolean, default=False)
    can_view_employee_details = db.Column(db.Boolean, default=False)
    can_edit_employees_data = db.Column(db.Boolean, default=False)
    can_add_new_employee = db.Column(db.Boolean, default=False)
    can_delete_employee = db.Column(db.Boolean, default=False)
    
    # School permissions
    can_view_schools_list = db.Column(db.Boolean, default=False)
    can_view_school_details = db.Column(db.Boolean, default=False)
    can_edit_schools_data = db.Column(db.Boolean, default=False)
    can_add_new_school = db.Column(db.Boolean, default=False)
    can_delete_school = db.Column(db.Boolean, default=False)
    
    # Leave permissions
    can_view_leaves_list = db.Column(db.Boolean, default=False)
    can_view_leave_details = db.Column(db.Boolean, default=False)
    can_edit_leaves_data = db.Column(db.Boolean, default=False)
    can_add_new_leave = db.Column(db.Boolean, default=False)
    can_delete_leave = db.Column(db.Boolean, default=False)
    can_manage_leave_balances = db.Column(db.Boolean, default=False)
    
    # Departure permissions
    can_view_departures_list = db.Column(db.Boolean, default=False)
    can_view_departure_details = db.Column(db.Boolean, default=False)
    can_edit_departures_data = db.Column(db.Boolean, default=False)
    can_add_new_departure = db.Column(db.Boolean, default=False)
    can_delete_departure = db.Column(db.Boolean, default=False)
    
    # Transfer permissions
    can_view_transfers_list = db.Column(db.Boolean, default=False)
    can_view_transfer_details = db.Column(db.Boolean, default=False)
    can_edit_transfers_data = db.Column(db.Boolean, default=False)
    can_add_new_transfer = db.Column(db.Boolean, default=False)
    can_delete_transfer = db.Column(db.Boolean, default=False)
    
    # Report permissions
    can_view_employee_reports = db.Column(db.Boolean, default=False)
    can_view_school_reports = db.Column(db.Boolean, default=False)
    can_view_comprehensive_reports = db.Column(db.Boolean, default=False)
    
    # Export permissions
    can_export_employee_data = db.Column(db.Boolean, default=False)
    can_export_school_data = db.Column(db.Boolean, default=False)
    can_export_report_data = db.Column(db.Boolean, default=False)
    
    # User management permissions
    can_view_users_list = db.Column(db.Boolean, default=False)
    can_add_new_user = db.Column(db.Boolean, default=False)
    can_manage_user_permissions = db.Column(db.Boolean, default=False)
    
    # Form permissions
    can_view_forms_list = db.Column(db.Boolean, default=False)
    can_edit_forms_data = db.Column(db.Boolean, default=False)
    can_add_new_form = db.Column(db.Boolean, default=False)
    can_delete_form = db.Column(db.Boolean, default=False)
    
    # System permissions
    can_view_system_logs = db.Column(db.Boolean, default=False)
    can_manage_system_settings = db.Column(db.Boolean, default=False)
    can_process_monthly_departures = db.Column(db.Boolean, default=False)
    
    # صلاحيات الموظفين المفصلة
    can_view_employees = db.Column(db.Boolean, default=False)
    can_add_employees = db.Column(db.Boolean, default=False)
    can_edit_employees = db.Column(db.Boolean, default=False)
    can_delete_employees = db.Column(db.Boolean, default=False)
    can_view_employee_details = db.Column(db.Boolean, default=False)
    
    # صلاحيات الإجازات المفصلة
    can_view_leaves = db.Column(db.Boolean, default=False)
    can_add_leaves = db.Column(db.Boolean, default=False)
    can_edit_leaves = db.Column(db.Boolean, default=False)
    can_delete_leaves = db.Column(db.Boolean, default=False)
    can_approve_leaves = db.Column(db.Boolean, default=False)
    can_manage_leave_balances = db.Column(db.Boolean, default=False)
    
    # صلاحيات المغادرات المفصلة
    can_view_departures = db.Column(db.Boolean, default=False)
    can_add_departures = db.Column(db.Boolean, default=False)
    can_edit_departures = db.Column(db.Boolean, default=False)
    can_delete_departures = db.Column(db.Boolean, default=False)
    can_convert_departures = db.Column(db.Boolean, default=False)
    
    # صلاحيات التقارير المفصلة
    can_view_employee_reports = db.Column(db.Boolean, default=False)
    can_view_school_reports = db.Column(db.Boolean, default=False)
    can_view_leave_reports = db.Column(db.Boolean, default=False)
    can_view_departure_reports = db.Column(db.Boolean, default=False)
    can_view_comprehensive_reports = db.Column(db.Boolean, default=False)
    
    # صلاحيات التصدير المفصلة
    can_export_employees = db.Column(db.Boolean, default=False)
    can_export_leaves = db.Column(db.Boolean, default=False)
    can_export_departures = db.Column(db.Boolean, default=False)
    can_export_balances = db.Column(db.Boolean, default=False)
    can_export_reports = db.Column(db.Boolean, default=False)
    
    # صلاحيات إدارية إضافية
    can_view_system_logs = db.Column(db.Boolean, default=False)
    can_manage_system_settings = db.Column(db.Boolean, default=False)
    can_view_statistics = db.Column(db.Boolean, default=False)
    
    # صلاحيات خاصة بالمدارس
    can_view_own_school_only = db.Column(db.Boolean, default=False)
    can_manage_school_employees = db.Column(db.Boolean, default=False)
    can_view_school_statistics = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def has_permission(self, permission):
        """Return a dictionary of all permissions for easy checking"""
        permission_map = {
            # Employee permissions
            'view_employees_list': self.can_view_employees_list or self.is_admin,
            'view_employee_details': self.can_view_employee_details or self.is_admin,
            'edit_employees_data': self.can_edit_employees_data or self.is_admin,
            'add_new_employee': self.can_add_new_employee or self.is_admin,
            'delete_employee': self.can_delete_employee or self.is_admin,
            
            # School permissions
            'view_schools_list': self.can_view_schools_list or self.is_admin,
            'view_school_details': self.can_view_school_details or self.is_admin,
            'edit_schools_data': self.can_edit_schools_data or self.is_admin,
            'add_new_school': self.can_add_new_school or self.is_admin,
            'delete_school': self.can_delete_school or self.is_admin,
            
            # Leave permissions
            'view_leaves_list': self.can_view_leaves_list or self.is_admin,
            'view_leave_details': self.can_view_leave_details or self.is_admin,
            'edit_leaves_data': self.can_edit_leaves_data or self.is_admin,
            'add_new_leave': self.can_add_new_leave or self.is_admin,
            'delete_leave': self.can_delete_leave or self.is_admin,
            'manage_leave_balances': self.can_manage_leave_balances or self.is_admin,
            
            # Departure permissions
            'view_departures_list': self.can_view_departures_list or self.is_admin,
            'view_departure_details': self.can_view_departure_details or self.is_admin,
            'edit_departures_data': self.can_edit_departures_data or self.is_admin,
            'add_new_departure': self.can_add_new_departure or self.is_admin,
            'delete_departure': self.can_delete_departure or self.is_admin,
            
            # Transfer permissions
            'view_transfers_list': self.can_view_transfers_list or self.is_admin,
            'view_transfer_details': self.can_view_transfer_details or self.is_admin,
            'edit_transfers_data': self.can_edit_transfers_data or self.is_admin,
            'add_new_transfer': self.can_add_new_transfer or self.is_admin,
            'delete_transfer': self.can_delete_transfer or self.is_admin,
            
            # Report permissions
            'view_employee_reports': self.can_view_employee_reports or self.is_admin,
            'view_school_reports': self.can_view_school_reports or self.is_admin,
            'view_comprehensive_reports': self.can_view_comprehensive_reports or self.is_admin,
            
            # Export permissions
            'export_employee_data': self.can_export_employee_data or self.is_admin,
            'export_school_data': self.can_export_school_data or self.is_admin,
            'export_report_data': self.can_export_report_data or self.is_admin,
            
            # User management permissions
            'view_users_list': self.can_view_users_list or self.is_admin,
            'add_new_user': self.can_add_new_user or self.is_admin,
            'manage_user_permissions': self.can_manage_user_permissions or self.is_admin,
            
            # Form permissions
            'view_forms_list': self.can_view_forms_list or self.is_admin,
            'edit_forms_data': self.can_edit_forms_data or self.is_admin,
            'add_new_form': self.can_add_new_form or self.is_admin,
            'delete_form': self.can_delete_form or self.is_admin,
            
            # System permissions
            'view_system_logs': self.can_view_system_logs or self.is_admin,
            'backup_database': self.can_backup_database or self.is_admin,
            'manage_system_settings': self.can_manage_system_settings or self.is_admin,
            'process_monthly_departures': self.can_process_monthly_departures or self.is_admin,
        }
        
        return permission_map.get(permission, False)

    def __repr__(self):
        return f'<User {self.username}>'

# في ملف models.py، أضف عمود جديد لجدول FormTemplate
class FormTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # اسم النموذج
    file_path = db.Column(db.String(255), nullable=False)  # مسار الملف
    file_type = db.Column(db.String(20), nullable=False)  # نوع الملف (Word, PDF, Image)
    description = db.Column(db.Text)  # وصف النموذج
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)  # تاريخ الرفع
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # المستخدم الذي قام بالرفع
    original_extension = db.Column(db.String(10))  # عمود جديد لحفظ الامتداد الأصلي
    
    # العلاقة مع المستخدم
    user = db.relationship('User', backref=db.backref('form_templates', lazy=True))
    
    def __repr__(self):
        return f'<FormTemplate {self.name}>'


class Leave(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)  # الموظف
    leave_type = db.Column(db.String(50), nullable=False)  # نوع الإجازة (سنوية، مرضية، طارئة، بدون راتب، إلخ)
    start_date = db.Column(db.Date, nullable=False)  # تاريخ بداية الإجازة
    end_date = db.Column(db.Date, nullable=False)  # تاريخ نهاية الإجازة
    days_count = db.Column(db.Integer, nullable=False)  # عدد أيام الإجازة
    start_time = db.Column(db.Time, nullable=True)  # وقت بداية المغادرة
    end_time = db.Column(db.Time, nullable=True)  # وقت نهاية المغادرة
    hours_count = db.Column(db.Float, nullable=True)  # عدد ساعات المغادرة
    reason = db.Column(db.Text)  # سبب الإجازة
    notes = db.Column(db.Text)  # ملاحظات
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # تاريخ الإنشاء
    
    def __repr__(self):
        if self.leave_type == 'مغادرة':
            return f'<Leave {self.employee.name} - {self.leave_type} - {self.hours_count} hours>'
        return f'<Leave {self.employee.name} - {self.leave_type} - {self.days_count} days>'


class LeaveBalance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)  # السنة
    current_year_balance = db.Column(db.Integer, default=30)  # رصيد السنة الحالية
    previous_year_balance = db.Column(db.Integer, default=0)  # رصيد السنة السابقة
    sick_leave_balance = db.Column(db.Integer, default=7)  # رصيد الإجازات المرضية
    used_annual_leave = db.Column(db.Integer, default=0)  # الإجازات السنوية المستخدمة
    used_sick_leave = db.Column(db.Integer, default=0)  # الإجازات المرضية المستخدمة
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # إزالة هذا السطر لأن العلاقة معرفة في Employee
    # employee = db.relationship('Employee', backref=db.backref('leave_balances', lazy=True))
    
    # فهرس فريد لضمان عدم تكرار السنة للموظف الواحد
    __table_args__ = (db.UniqueConstraint('employee_id', 'year', name='unique_employee_year'),)
    
    def get_remaining_annual_balance(self):
        """حساب الرصيد المتبقي من الإجازات السنوية"""
        current_balance = self.current_year_balance or 0
        previous_balance = self.previous_year_balance or 0
        used_leave = self.used_annual_leave or 0
        return (current_balance + previous_balance) - used_leave
    
    def get_remaining_sick_balance(self):
        """حساب الرصيد المتبقي من الإجازات المرضية"""
        sick_balance = self.sick_leave_balance or 0
        used_sick = self.used_sick_leave or 0
        return sick_balance - used_sick
    
    def __repr__(self):
        return f'<LeaveBalance {self.employee.name} - {self.year}>'

class ConvertedDeparture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    original_departure_date = db.Column(db.Date, nullable=False)  # تاريخ المغادرة الأصلي
    original_start_time = db.Column(db.Time, nullable=False)  # وقت بداية المغادرة الأصلي
    original_end_time = db.Column(db.Time, nullable=False)  # وقت نهاية المغادرة الأصلي
    original_hours_count = db.Column(db.Float, nullable=False)  # عدد ساعات المغادرة الأصلي
    converted_to_leave_type = db.Column(db.String(50), nullable=False)  # نوع الإجازة المحولة إليها
    converted_days_count = db.Column(db.Integer, nullable=False)  # عدد أيام الإجازة المحولة
    original_reason = db.Column(db.Text)  # سبب المغادرة الأصلي
    original_notes = db.Column(db.Text)  # ملاحظات المغادرة الأصلية
    conversion_date = db.Column(db.DateTime, default=datetime.utcnow)  # تاريخ التحويل
    leave_id = db.Column(db.Integer, db.ForeignKey('leave.id'), nullable=True)  # ربط مع سجل الإجازة المحولة
    
    # إزالة هذا السطر لأن العلاقة معرفة في Employee
    # employee = db.relationship('Employee', backref=db.backref('converted_departures', lazy=True))
    converted_leave = db.relationship('Leave', backref=db.backref('original_departure', uselist=False))
    
    def __repr__(self):
        return f'<ConvertedDeparture {self.employee.name} - {self.original_hours_count} hours to {self.converted_days_count} days>'

class MonthlyDepartureBalance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    total_hours = db.Column(db.Float, default=0.0)  # إجمالي ساعات المغادرات في الشهر
    converted_days = db.Column(db.Integer, default=0)  # الأيام المحولة (كل 7 ساعات = يوم)
    remaining_hours = db.Column(db.Float, default=0.0)  # الساعات المتبقية للشهر التالي
    carried_hours = db.Column(db.Float, default=0.0)  # الساعات المنقولة من الشهر السابق
    processed = db.Column(db.Boolean, default=False)  # هل تم معالجة الشهر
    processing_date = db.Column(db.DateTime)  # تاريخ المعالجة
    
    # إزالة هذا السطر لأن العلاقة معرفة في Employee
    # employee = db.relationship('Employee', backref=db.backref('monthly_departure_balances', lazy=True))
    
    def __repr__(self):
        return f'<MonthlyDepartureBalance {self.employee.name} - {self.year}/{self.month}>'


class TechnicalDeficiency(db.Model):
    """نموذج لحفظ بيانات النقص الفني اليدوي"""
    __tablename__ = 'technical_deficiencies'
    
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)  # Changed from 'schools.id' to 'school.id'
    specialization = db.Column(db.String(200), nullable=False)
    job_title = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(200), nullable=True)
    required_count = db.Column(db.Integer, nullable=False, default=0)
    current_count = db.Column(db.Integer, nullable=False, default=0)
    deficiency_count = db.Column(db.Integer, nullable=False, default=0)
    # حقول النواقص
    deficiency_bachelor = db.Column(db.Integer, nullable=False, default=0)
    deficiency_diploma = db.Column(db.Integer, nullable=False, default=0)
    # حقول الزوائد
    surplus_bachelor = db.Column(db.Integer, nullable=False, default=0)
    surplus_diploma = db.Column(db.Integer, nullable=False, default=0)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    school = db.relationship('School', backref=db.backref('technical_deficiencies', lazy=True))
    
    def __repr__(self):
        return f'<TechnicalDeficiency {self.school.name} - {self.specialization}>'


class UserLog(db.Model):
    """نموذج لتتبع أنشطة المستخدمين في النظام"""
    __tablename__ = 'user_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)  # نوع العملية (تسجيل دخول، إضافة موظف، تعديل، حذف، إلخ)
    module = db.Column(db.String(50), nullable=False)  # الوحدة (الموظفين، المدارس، الإجازات، إلخ)
    description = db.Column(db.Text, nullable=True)  # وصف تفصيلي للعملية
    target_id = db.Column(db.Integer, nullable=True)  # معرف العنصر المستهدف (إن وجد)
    target_type = db.Column(db.String(50), nullable=True)  # نوع العنصر المستهدف (موظف، مدرسة، إلخ)
    ip_address = db.Column(db.String(45), nullable=True)  # عنوان IP
    user_agent = db.Column(db.Text, nullable=True)  # معلومات المتصفح
    status = db.Column(db.String(20), default='success')  # حالة العملية (نجح، فشل)
    error_message = db.Column(db.Text, nullable=True)  # رسالة الخطأ في حالة الفشل
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    user = db.relationship('User', backref=db.backref('logs', lazy=True, order_by='UserLog.created_at.desc()'))
    
    def __repr__(self):
        return f'<UserLog {self.user.username} - {self.action} - {self.module}>'