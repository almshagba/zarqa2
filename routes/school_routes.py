from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import db
from utils import log_user_activity
from models import School, Employee
from routes.auth_routes import admin_required, login_required, permission_required
from constants import DIRECTORATE_DEPARTMENTS, REGIONS

school = Blueprint('school', __name__)

# صفحة المدارس
@school.route('/schools')
def schools():
    # الحصول على معاملات البحث والفلترة
    search_term = request.args.get('search', '')
    gender_filter = request.args.get('gender', '')
    region_filter = request.args.get('region', '')
    
    # بناء الاستعلام الأساسي - فلترة المدارس فقط (استبعاد الأقسام الإدارية)
    query = School.query.filter(
        ~School.name.in_(DIRECTORATE_DEPARTMENTS)
    )
    
    # تطبيق البحث بالاسم
    if search_term:
        query = query.filter(School.name.contains(search_term))
    
    # تطبيق فلترة الجنس
    if gender_filter:
        query = query.filter(School.gender == gender_filter)
    
    # تطبيق فلترة المنطقة
    if region_filter:
        query = query.filter(School.region == region_filter)
    
    # ترتيب النتائج
    schools = query.order_by(
        School.gender.asc(),  # ترتيب حسب الجنس أولاً
        School.name.asc()     # ثم حسب الاسم
    ).all()
    
    # الحصول على قائمة الأجناس والمناطق المتاحة للفلترة
    available_genders = db.session.query(School.gender).filter(
        ~School.name.in_(DIRECTORATE_DEPARTMENTS),
        School.gender.isnot(None)
    ).distinct().all()
    available_genders = [g[0] for g in available_genders if g[0]]
    
    available_regions = db.session.query(School.region).filter(
        ~School.name.in_(DIRECTORATE_DEPARTMENTS),
        School.region.isnot(None)
    ).distinct().all()
    available_regions = [r[0] for r in available_regions if r[0]]
    
    return render_template('schools.html', 
                         schools=schools,
                         search_term=search_term,
                         gender_filter=gender_filter,
                         region_filter=region_filter,
                         available_genders=available_genders,
                         available_regions=available_regions,
                         regions=REGIONS)

# إضافة مدرسة جديدة
@school.route('/schools/add', methods=['GET', 'POST'])
@permission_required('can_manage_schools')
def add_school():
    if request.method == 'POST':
        name = request.form.get('name')
        school_type = request.form.get('school_type')
        location = request.form.get('location')
        gender = request.form.get('gender')
        region = request.form.get('region')
        
        # التحقق من عدم وجود مدرسة بنفس الاسم
        existing_school = School.query.filter_by(name=name).first()
        if existing_school:
            flash('يوجد مدرسة بنفس الاسم', 'danger')
        else:
            # حوالي السطر 79
            school = School(
                name=name, 
                phone=request.form.get('phone', ''),  # إضافة رقم الهاتف إذا كان متوفراً
                address=request.form.get('address', ''),  # إضافة العنوان إذا كان متوفراً
                gender=gender,
                region=region
            )
            db.session.add(school)
            db.session.commit()
            
            # تسجيل العملية في سجلات المستخدمين
            log_user_activity(
                user_id=session.get('user_id'),
                action='إضافة',
                module='المدارس',
                description=f'تم إضافة المدرسة: {name}',
                target_id=school.id,
                target_type='مدرسة'
            )
            
            flash('تمت إضافة المدرسة بنجاح', 'success')
            return redirect(url_for('school.schools'))
    
    return render_template('school_form.html')

@school.route('/schools/edit/<int:id>', methods=['GET', 'POST'])
@permission_required('can_manage_schools')
def edit_school(id):
    school = School.query.get_or_404(id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        school_type = request.form.get('school_type')
        location = request.form.get('location')
        gender = request.form.get('gender')
        region = request.form.get('region')
        
        # التحقق من عدم وجود مدرسة أخرى بنفس الاسم
        existing_school = School.query.filter_by(name=name).first()
        if existing_school and existing_school.id != id:
            flash('يوجد مدرسة أخرى بنفس الاسم', 'danger')
        else:
            school.name = name
            school.school_type = school_type
            school.location = location
            school.gender = gender
            school.region = region
            db.session.commit()
            
            # تسجيل العملية في سجلات المستخدمين
            log_user_activity(
                user_id=session.get('user_id'),
                action='تعديل',
                module='المدارس',
                description=f'تم تعديل المدرسة: {school.name}',
                target_id=school.id,
                target_type='مدرسة'
            )
            
            flash('تم تحديث المدرسة بنجاح', 'success')
            return redirect(url_for('school.schools'))
    
    return render_template('school_form.html', school=school)

# حذف مدرسة
@school.route('/schools/delete/<int:id>')
# استبدال @admin_required بـ:
@permission_required('can_manage_schools')
def delete_school(id):
    school = School.query.get_or_404(id)
    school_name = school.name  # حفظ الاسم قبل الحذف
    
    # التحقق من عدم وجود موظفين مرتبطين بالمدرسة
    employees = Employee.query.filter_by(school_id=id).first()
    if employees:
        flash('لا يمكن حذف المدرسة لوجود موظفين مرتبطين بها', 'danger')
        return redirect(url_for('school.schools'))
    
    db.session.delete(school)
    db.session.commit()
    
    # تسجيل العملية في سجلات المستخدمين
    log_user_activity(
        user_id=session.get('user_id'),
        action='حذف',
        module='المدارس',
        description=f'تم حذف المدرسة: {school_name}',
        target_id=id,
        target_type='مدرسة'
    )
    
    flash('تم حذف المدرسة بنجاح', 'success')
    return redirect(url_for('school.schools'))