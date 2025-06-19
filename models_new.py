from database import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Numeric

# جدول الصلاحيات
class Permission(db.Model):
    __tablename__ = 'permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)  # اسم الصلاحية
    display_name = db.Column(db.String(200), nullable=False)  # الاسم المعروض
    description = db.Column(db.Text)  # وصف الصلاحية
    category = db.Column(db.String(50), nullable=False)  # فئة الصلاحية (employees, schools, reports, etc.)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Permission {self.name}>'

# جدول الأدوار
class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)  # اسم الدور
    display_name = db.Column(db.String(200), nullable=False)  # الاسم المعروض
    description = db.Column(db.Text)  # وصف الدور
    is_admin = db.Column(db.Boolean, default=False)  # هل هذا دور إداري
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # العلاقة مع الصلاحيات
    permissions = db.relationship('Permission', secondary='role_permissions', backref='roles')
    
    def __repr__(self):
        return f'<Role {self.name}>'
    
    def has_permission(self, permission_name):
        """فحص ما إذا كان الدور يملك صلاحية معينة"""
        if self.is_admin:
            return True
        return any(perm.name == permission_name and perm.is_active for perm in self.permissions)

# جدول ربط الأدوار بالصلاحيات
role_permissions = db.Table('role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)

# جدول ربط المستخدمين بالأدوار
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
    db.Column('assigned_at', db.DateTime, default=datetime.utcnow),
    db.Column('assigned_by', db.Integer, db.ForeignKey('users.id'))
)

# تحديث جدول المستخدمين
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # العلاقة مع الأدوار
    roles = db.relationship('Role', secondary=user_roles, backref='users')
    
    def set_password(self, password):
        """تشفير كلمة المرور"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """التحقق من كلمة المرور"""
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_admin(self):
        """فحص ما إذا كان المستخدم مديراً"""
        return any(role.is_admin for role in self.roles if role.is_active)
    
    def has_permission(self, permission_name):
        """فحص ما إذا كان المستخدم يملك صلاحية معينة"""
        if not self.is_active:
            return False
            
        # المدير لديه جميع الصلاحيات
        if self.is_admin:
            return True
            
        # فحص الصلاحيات من خلال الأدوار
        for role in self.roles:
            if role.is_active and role.has_permission(permission_name):
                return True
                
        return False
    
    def get_all_permissions(self):
        """الحصول على جميع صلاحيات المستخدم"""
        if self.is_admin:
            return Permission.query.filter_by(is_active=True).all()
            
        permissions = set()
        for role in self.roles:
            if role.is_active:
                permissions.update(role.permissions)
                
        return list(permissions)
    
    def add_role(self, role):
        """إضافة دور للمستخدم"""
        if role not in self.roles:
            self.roles.append(role)
    
    def remove_role(self, role):
        """إزالة دور من المستخدم"""
        if role in self.roles:
            self.roles.remove(role)
    
    def __repr__(self):
        return f'<User {self.username}>'

# باقي النماذج تبقى كما هي...
class School(db.Model):
    __tablename__ = 'schools'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    address = db.Column(db.Text)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    principal_name = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<School {self.name}>'

class Employee(db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_number = db.Column(db.String(50), unique=True, nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    national_id = db.Column(db.String(20), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    job_title = db.Column(db.String(100))
    department = db.Column(db.String(100))
    hire_date = db.Column(db.Date)
    salary = db.Column(Numeric(10, 2))
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    school = db.relationship('School', backref='employees')
    
    def __repr__(self):
        return f'<Employee {self.full_name}>'