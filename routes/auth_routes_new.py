from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import db
from models_new import User, Role, Permission
from auth_decorators import permission_required, admin_required, login_required
from utils import log_user_activity

auth = Blueprint('auth', __name__)

@auth.route('/users')
@permission_required('users.view')
def users():
    users = User.query.all()
    return render_template('users.html', users=users)

@auth.route('/users/add', methods=['GET', 'POST'])
@permission_required('users.create')
def add_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        selected_roles = request.form.getlist('roles')
        
        # التحقق من عدم وجود مستخدم بنفس اسم المستخدم
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('اسم المستخدم موجود بالفعل', 'danger')
        else:
            # إنشاء المستخدم الجديد
            new_user = User(
                username=username,
                full_name=full_name,
                email=email,
                phone=phone
            )
            new_user.set_password(password)
            
            # إضافة الأدوار المحددة
            for role_id in selected_roles:
                role = Role.query.get(role_id)
                if role:
                    new_user.add_role(role)
            
            db.session.add(new_user)
            db.session.commit()
            
            log_user_activity(session['user_id'], 'إضافة مستخدم جديد', f'تم إضافة المستخدم: {username}')
            flash('تم إضافة المستخدم بنجاح', 'success')
            return redirect(url_for('auth.users'))
    
    # الحصول على جميع الأدوار للعرض في النموذج
    roles = Role.query.filter_by(is_active=True).all()
    return render_template('add_user.html', roles=roles)

@auth.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@permission_required('users.edit')
def edit_user(id):
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        selected_roles = request.form.getlist('roles')
        
        # التحقق من عدم وجود مستخدم آخر بنفس اسم المستخدم
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != id:
            flash('اسم المستخدم موجود بالفعل', 'danger')
        else:
            # تحديث بيانات المستخدم
            user.username = username
            user.full_name = full_name
            user.email = email
            user.phone = phone
            
            if password:
                user.set_password(password)
            
            # تحديث الأدوار
            user.roles.clear()
            for role_id in selected_roles:
                role = Role.query.get(role_id)
                if role:
                    user.add_role(role)
            
            db.session.commit()
            
            log_user_activity(session['user_id'], 'تعديل مستخدم', f'تم تعديل المستخدم: {username}')
            flash('تم تحديث المستخدم بنجاح', 'success')
            return redirect(url_for('auth.users'))
    
    roles = Role.query.filter_by(is_active=True).all()
    return render_template('edit_user.html', user=user, roles=roles)

@auth.route('/roles')
@admin_required
def roles():
    roles = Role.query.all()
    return render_template('roles.html', roles=roles)

@auth.route('/roles/add', methods=['GET', 'POST'])
@admin_required
def add_role():
    if request.method == 'POST':
        name = request.form.get('name')
        display_name = request.form.get('display_name')
        description = request.form.get('description')
        selected_permissions = request.form.getlist('permissions')
        
        # التحقق من عدم وجود دور بنفس الاسم
        existing_role = Role.query.filter_by(name=name).first()
        if existing_role:
            flash('اسم الدور موجود بالفعل', 'danger')
        else:
            # إنشاء الدور الجديد
            new_role = Role(
                name=name,
                display_name=display_name,
                description=description
            )
            
            # إضافة الصلاحيات المحددة
            for permission_id in selected_permissions:
                permission = Permission.query.get(permission_id)
                if permission:
                    new_role.permissions.append(permission)
            
            db.session.add(new_role)
            db.session.commit()
            
            log_user_activity(session['user_id'], 'إضافة دور جديد', f'تم إضافة الدور: {name}')
            flash('تم إضافة الدور بنجاح', 'success')
            return redirect(url_for('auth.roles'))
    
    # تجميع الصلاحيات حسب الفئة
    permissions_by_category = {}
    permissions = Permission.query.filter_by(is_active=True).all()
    for permission in permissions:
        if permission.category not in permissions_by_category:
            permissions_by_category[permission.category] = []
        permissions_by_category[permission.category].append(permission)
    
    return render_template('add_role.html', permissions_by_category=permissions_by_category)