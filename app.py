from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, current_user
from database import db
from config import config
import os
# استيراد البلوبرنت من الملفات الجديدة
from routes.main_routes import main
from routes.auth_routes import auth
from routes.leave_routes import leave
from routes.school_routes import school
from routes.employee_routes import employee
from routes.report_routes import report
from routes.export_routes import export
from routes.admin_routes import admin
from routes.principal_leaves_routes import principal_leaves
from new_user_routes import new_user_bp
from routes.procedures_routes import procedures
from datetime import datetime
from models import Employee, School, Transfer, User, FormTemplate, Leave, UserLog
from utils import log_user_activity
# احذف هذا السطر إذا كان موجوداً:
# from flask_login import current_user

app = Flask(__name__)

# تحديد بيئة التشغيل
config_name = os.environ.get('FLASK_ENV', 'default')
app.config.from_object(config[config_name])

db.init_app(app)

# تهيئة Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'يرجى تسجيل الدخول للوصول إلى هذه الصفحة.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# تسجيل المسارات
app.register_blueprint(main)
app.register_blueprint(auth)
app.register_blueprint(leave)  # تسجيل بلوبرنت الإجازات والمغادرات
app.register_blueprint(school)  # تسجيل بلوبرنت المدارس
app.register_blueprint(employee)  # تسجيل بلوبرنت الموظفين
app.register_blueprint(report)  # تسجيل بلوبرنت التقارير
app.register_blueprint(export)  # تسجيل بلوبرنت التقارير
app.register_blueprint(admin)  # تسجيل بلوبرنت الإدارة
app.register_blueprint(new_user_bp, url_prefix='/new_users')
app.register_blueprint(principal_leaves)  # تسجيل بلوبرنت الإجازات العرضية للمدراء
app.register_blueprint(procedures)  # تسجيل بلوبرنت الإجراءات

# إضافة متغير now إلى جميع القوالب
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# إضافة دالة للحصول على المستخدم الحالي
@app.context_processor
def inject_user():
    current_user = None
    if 'user_id' in session:
        current_user = User.query.get(session['user_id'])
    return dict(current_user=current_user)

# إضافة فلتر strftime لتنسيق التاريخ
@app.template_filter('strftime')
def _jinja2_filter_strftime(date, fmt=None):
    if fmt:
        return date.strftime(fmt)
    return date.strftime('%Y')

# التحقق من حالة تسجيل الدخول
@app.before_request
def check_login():
    # قائمة المسارات المسموح بها بدون تسجيل دخول
    allowed_routes = ['auth.login', 'static']
    
    # التحقف من وجود جلسة مستخدم نشطة
    if 'user_id' not in session and request.endpoint and not any(request.endpoint.startswith(route) for route in allowed_routes):
        return redirect(url_for('auth.login'))

# إنشاء سياق التطبيق وإنشاء الجداول
with app.app_context():
    db.create_all()
    
    # إنشاء مستخدم مسؤول افتراضي إذا لم يكن موجودًا
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', full_name='مدير النظام', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)