from functools import wraps
from flask import session, flash, redirect, url_for, request
from models import User

def permission_required(permission_name):
    """ديكوريتر للتحقق من الصلاحيات - النسخة المحدثة"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # التحقق من تسجيل الدخول
            if 'user_id' not in session:
                flash('يرجى تسجيل الدخول أولاً', 'danger')
                return redirect(url_for('auth.login'))
            
            # الحصول على المستخدم
            user = User.query.get(session['user_id'])
            if not user or not user.is_active:
                flash('المستخدم غير موجود أو غير نشط', 'danger')
                session.clear()
                return redirect(url_for('auth.login'))
            
            # التحقق من الصلاحية
            if not user.has_permission(permission_name):
                flash(f'ليس لديك صلاحية للوصول إلى هذه الصفحة. الصلاحية المطلوبة: {permission_name}', 'danger')
                return redirect(url_for('main.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """ديكوريتر للتحقق من صلاحيات المدير"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('يرجى تسجيل الدخول أولاً', 'danger')
            return redirect(url_for('auth.login'))
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function

def login_required(f):
    """ديكوريتر للتحقق من تسجيل الدخول فقط"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('يرجى تسجيل الدخول أولاً', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def multiple_permissions_required(*permission_names, require_all=True):
    """ديكوريتر للتحقق من عدة صلاحيات
    
    Args:
        permission_names: قائمة بأسماء الصلاحيات
        require_all: إذا كان True، يتطلب جميع الصلاحيات. إذا كان False، يتطلب صلاحية واحدة على الأقل
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('يرجى تسجيل الدخول أولاً', 'danger')
                return redirect(url_for('auth.login'))
            
            user = User.query.get(session['user_id'])
            if not user or not user.is_active:
                flash('المستخدم غير موجود أو غير نشط', 'danger')
                session.clear()
                return redirect(url_for('auth.login'))
            
            if require_all:
                # يتطلب جميع الصلاحيات
                missing_permissions = [perm for perm in permission_names if not user.has_permission(perm)]
                if missing_permissions:
                    flash(f'ليس لديك الصلاحيات المطلوبة: {", ".join(missing_permissions)}', 'danger')
                    return redirect(url_for('main.index'))
            else:
                # يتطلب صلاحية واحدة على الأقل
                has_any_permission = any(user.has_permission(perm) for perm in permission_names)
                if not has_any_permission:
                    flash(f'ليس لديك أي من الصلاحيات المطلوبة: {", ".join(permission_names)}', 'danger')
                    return redirect(url_for('main.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator