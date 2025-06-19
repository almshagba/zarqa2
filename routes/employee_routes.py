from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from database import db
from utils import log_user_activity
from models import Employee, School, Transfer, User  # إضافة User هنا
from datetime import datetime
from sqlalchemy import func
import os
from werkzeug.utils import secure_filename
from constants import JOB_TITLES, DIRECTORATE_JOB_TITLES, DIRECTORATE_DEPARTMENTS
from io import BytesIO
import pandas as pd
from routes.auth_routes import admin_required
from .auth_routes import permission_required
from routes.auth_routes import login_required, permission_required

employee = Blueprint('employee', __name__)

# صفحة الموظفين
@employee.route('/employees')
def employees():
    # الحصول على قائمة الموظفين مع إمكانية البحث والتصفية
    search_term = request.args.get('search', '')
    job_filter = request.args.get('job_title', '')
    school_filter = request.args.get('school_id', '')
    
    # إضافة دعم الصفحات - الحصول على رقم الصفحة الحالية
    page = request.args.get('page', 1, type=int)
    per_page = 25  # عدد الموظفين في كل صفحة
    
    # تصفية الموظفين لإظهار موظفي المدارس فقط (ليس موظفي المديرية)
    query = Employee.query.filter_by(is_directorate_employee=False)
    
    if search_term:
        query = query.filter(
            (Employee.name.ilike(f'%{search_term}%')) |
            (Employee.ministry_number.ilike(f'%{search_term}%'))
        )
    
    if job_filter:
        query = query.filter(Employee.job_title == job_filter)
    
    if school_filter:
        query = query.filter(Employee.school_id == school_filter)
    
    # استخدام paginate بدلاً من all() للصعول على نتائج مقسمة إلى صفحات
    paginated_employees = query.order_by(Employee.name).paginate(page=page, per_page=per_page, error_out=False)
    
    # تصفية المدارس لإزالة أقسام المديرية من قائمة التصفية
    from constants import DIRECTORATE_DEPARTMENTS
    schools = School.query.filter(~School.name.in_(DIRECTORATE_DEPARTMENTS)).order_by(School.name).all()
    
    # الحصول على إجمالي عدد الموظفين للإحصائيات
    total_employees = Employee.query.filter_by(is_directorate_employee=False).count()
    total_male = Employee.query.filter_by(is_directorate_employee=False, gender='ذكر').count()
    total_female = Employee.query.filter(
        Employee.is_directorate_employee == False,
        (Employee.gender == 'أنثى') | (Employee.gender == 'انثى')
    ).count()
    
    return render_template('employees.html', 
                         employees=paginated_employees.items, 
                         pagination=paginated_employees,
                         schools=schools, 
                         job_titles=JOB_TITLES,
                         search_term=search_term,
                         selected_school=int(school_filter) if school_filter else None,
                         selected_job=job_filter,
                         total_employees=total_employees,
                         total_male=total_male,
                         total_female=total_female)

# إضافة موظف جديد
@employee.route('/employees/add', methods=['GET', 'POST'])
@permission_required('can_manage_employees')
def add_employee():
    from constants import DIRECTORATE_DEPARTMENTS
    
    if request.method == 'POST':
        # استخراج البيانات من النموذج
        name = request.form.get('name')
        civil_id = request.form.get('civil_id')
        ministry_number = request.form.get('ministry_number')
        job_title = request.form.get('job_title')
        school_id = request.form.get('school_id')
        phone_number = request.form.get('phone_number')
        gender = request.form.get('gender')
        qualification = request.form.get('qualification')
        appointment_date = request.form.get('appointment_date')
        
        # التحقق من الحقول المطلوبة
        if not all([name, civil_id, ministry_number, job_title, school_id, gender, qualification, appointment_date]):
            flash('جميع الحقول المطلوبة يجب أن تكون مملوءة', 'danger')
            from constants import DIRECTORATE_DEPARTMENTS
            schools = School.query.filter(~School.name.in_(DIRECTORATE_DEPARTMENTS)).order_by(School.name).all()
            return render_template('employee_form.html', employee=None, schools=schools, job_titles=JOB_TITLES, is_directorate=False)
        
        # التحقق من عدم وجود موظف بنفس الرقم المدني
        existing_employee_civil = Employee.query.filter_by(civil_id=civil_id).first()
        if existing_employee_civil:
            flash('يوجد موظف بنفس الرقم المدني', 'danger')
            from constants import DIRECTORATE_DEPARTMENTS
            schools = School.query.filter(~School.name.in_(DIRECTORATE_DEPARTMENTS)).order_by(School.name).all()
            return render_template('employee_form.html', employee=None, schools=schools, job_titles=JOB_TITLES, is_directorate=False)
        
        # التحقق من عدم وجود موظف بنفس الرقم الوزاري
        existing_employee_ministry = Employee.query.filter_by(ministry_number=ministry_number).first()
        if existing_employee_ministry:
            flash('يوجد موظف بنفس الرقم الوزاري', 'danger')
            from constants import DIRECTORATE_DEPARTMENTS
            schools = School.query.filter(~School.name.in_(DIRECTORATE_DEPARTMENTS)).order_by(School.name).all()
            return render_template('employee_form.html', employee=None, schools=schools, job_titles=JOB_TITLES, is_directorate=False)
        
        # تحويل تاريخ التعيين من نص إلى تاريخ
        try:
            appointment_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
        except ValueError:
            flash('تاريخ التعيين غير صحيح', 'danger')
            from constants import DIRECTORATE_DEPARTMENTS
            schools = School.query.filter(~School.name.in_(DIRECTORATE_DEPARTMENTS)).order_by(School.name).all()
            return render_template('employee_form.html', employee=None, schools=schools, job_titles=JOB_TITLES, is_directorate=False)
        
        # التحقق من أن القسم المختار من أقسام المديرية
        selected_school = School.query.get(int(school_id))
        is_directorate = selected_school.name in DIRECTORATE_DEPARTMENTS if selected_school else False
        
        # إنشاء موظف مديرية جديد
        employee = Employee(
            name=name,
            civil_id=civil_id,
            ministry_number=ministry_number,
            job_title=job_title,
            school_id=int(school_id),
            phone_number=phone_number,
            gender=gender,
            qualification=qualification,
            appointment_date=appointment_date,
            is_directorate_employee=is_directorate,  # تحديد حسب القسم الفعلي
           
        )
        db.session.add(employee)
        db.session.commit()
        
        # تسجيل العملية في سجلات المستخدمين
        log_user_activity(
            user_id=session.get('user_id'),
            action='إضافة',
            module='الموظفين',
            description=f'تم إضافة الموظف: {name}',
            target_id=employee.id,
            target_type='موظف'
        )
        
        flash('تم إضافة الموظف بنجاح', 'success')
        return redirect(url_for('employee.employees'))
    
    # الحصول على قائمة المدارس فقط (بدون أقسام المديرية) للـ GET request
    from constants import DIRECTORATE_DEPARTMENTS
    schools = School.query.filter(~School.name.in_(DIRECTORATE_DEPARTMENTS)).order_by(School.name).all()
    
    return render_template('employee_form.html', employee=None, schools=schools, job_titles=JOB_TITLES, is_directorate=False)

# تعديل بيانات موظف
@employee.route('/employees/edit/<int:id>', methods=['GET', 'POST'])
def edit_employee(id):
    employee = Employee.query.get_or_404(id)
    
    if request.method == 'POST':
        # الحصول على بيانات الموظف من النموذج
        ministry_number = request.form.get('ministry_number')
        name = request.form.get('name')
        civil_id = request.form.get('civil_id')
        phone_number = request.form.get('phone_number')
        gender = request.form.get('gender')
        job_title = request.form.get('job_title')
        qualification = request.form.get('qualification')
        bachelor_specialization = request.form.get('bachelor_specialization')
        high_diploma_specialization = request.form.get('high_diploma_specialization')
        masters_specialization = request.form.get('masters_specialization')
        phd_specialization = request.form.get('phd_specialization')
        subject = request.form.get('subject')
        appointment_date = request.form.get('appointment_date')
        school_id = request.form.get('school_id')
        
        # التحقق من عدم وجود موظف آخر بنفس الرقم المدني
        existing_employee = Employee.query.filter_by(civil_id=civil_id).first()
        if existing_employee and existing_employee.id != id:
            flash('يوجد موظف آخر بنفس الرقم المدني', 'danger')
        else:
            # تحديث بيانات الموظف
            employee.ministry_number = ministry_number
            employee.name = name
            employee.civil_id = civil_id
            employee.phone_number = phone_number
            employee.gender = gender
            employee.job_title = job_title
            employee.qualification = qualification
            employee.bachelor_specialization = bachelor_specialization
            employee.high_diploma_specialization = high_diploma_specialization
            employee.masters_specialization = masters_specialization
            employee.phd_specialization = phd_specialization
            employee.subject = subject
            if appointment_date:
                from datetime import datetime
                employee.appointment_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
            employee.school_id = school_id
            
            db.session.commit()
            
            # تسجيل العملية في سجلات المستخدمين
            log_user_activity(
                user_id=session.get('user_id'),
                action='تعديل',
                module='الموظفين',
                description=f'تم تعديل بيانات الموظف: {employee.name}',
                target_id=employee.id,
                target_type='موظف'
            )
            
            flash('تم تحديث بيانات الموظف بنجاح', 'success')
            return redirect(url_for('employee.employees'))
    
    # الحصول على قائمة المدارس للاختيار
    schools = School.query.order_by(School.name).all()
    
    # تحديد نوع الموظف وإرسال البيانات المناسبة
    if employee.is_directorate_employee:
        from constants import DIRECTORATE_DEPARTMENTS
        schools = School.query.filter(School.name.in_(DIRECTORATE_DEPARTMENTS)).order_by(School.name).all()
        job_titles = DIRECTORATE_JOB_TITLES
        is_directorate = True
    else:
        from constants import DIRECTORATE_DEPARTMENTS
        schools = School.query.filter(~School.name.in_(DIRECTORATE_DEPARTMENTS)).order_by(School.name).all()
        job_titles = JOB_TITLES
        is_directorate = False
    
    return render_template('employee_form.html', employee=employee, schools=schools, job_titles=job_titles, is_directorate=is_directorate)

# عرض بيانات موظف
@employee.route('/employees/view/<int:id>')
def view_employee(id):
    employee = Employee.query.get_or_404(id)
    
    # استخدام قالب مختلف بناءً على نوع الموظف
    if employee.is_directorate_employee:
        return render_template('directorate_employee_view.html', employee=employee)
    else:
        return render_template('employee_view.html', employee=employee)

# حذف موظف
@employee.route('/employees/delete/<int:id>', methods=['GET', 'POST'])
@permission_required('can_delete_employee')  # تغيير من can_manage_employees إلى can_delete_employee
def delete_employee(id):
    # التحقق الإضافي من صلاحية الحذف
    user = User.query.get(session['user_id'])
    if not user.is_admin and not getattr(user, 'can_delete_employee', False):
        flash('ليس لديك صلاحية لحذف الموظفين', 'danger')
        return redirect(url_for('employee.employees'))
    
    employee = Employee.query.get_or_404(id)
    employee_name = employee.name
    
    db.session.delete(employee)
    db.session.commit()
    
    # تسجيل العملية في سجلات المستخدمين
    log_user_activity(
        user_id=session.get('user_id'),
        action='حذف',
        module='الموظفين',
        description=f'تم حذف الموظف: {employee_name}',
        target_id=id,
        target_type='موظف'
    )
    
    flash('تم حذف الموظف بنجاح', 'success')
    return redirect(url_for('employee.employees'))

# تصدير بيانات الموظفين
@employee.route('/employees/export', methods=['GET', 'POST'])
@permission_required('can_manage_employees')
def export_employees():
    if request.method == 'POST':
        # الحصول على معايير التصفية
        job_filter = request.form.get('job')
        school_filter = request.form.get('school')
        directorate_filter = request.form.get('directorate')
        
        query = Employee.query
        
        if job_filter:
            query = query.filter(Employee.job_title == job_filter)
        
        if school_filter:
            query = query.filter(Employee.school_id == school_filter)
        
        if directorate_filter:
            if directorate_filter == 'directorate':
                query = query.filter(Employee.is_directorate_employee == True)
            elif directorate_filter == 'school':
                query = query.filter(Employee.is_directorate_employee == False)
        
        employees = query.order_by(Employee.name).all()
        
        # إنشاء DataFrame من بيانات الموظفين
        data = []
        for emp in employees:
            school_name = emp.school.name if emp.school else ''
            data.append({
                'الاسم': emp.name,
                'الرقم المدني': emp.civil_id,
                'رقم الملف': emp.ministry_number,
                'المسمى الوظيفي': emp.job_title,
                'المدرسة': school_name,
                'رقم الهاتف': emp.phone_number or '',
                'المديرية': 'نعم' if emp.is_directorate_employee else 'لا'
            })
        
        df = pd.DataFrame(data)
        
        # تصدير البيانات إلى ملف Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='الموظفين')
        
        output.seek(0)
        
        return send_file(
            output,
            as_attachment=True,
            download_name='employees_data.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    
    schools = School.query.order_by(School.name).all()
    return render_template('employee_data_export.html', schools=schools, job_titles=JOB_TITLES)

# صفحة موظفي المديرية
@employee.route('/directorate_employees')
def directorate_employees():
    try:
        search_term = request.args.get('search', '')
        job_filter = request.args.get('job', '')
        school_filter = request.args.get('school', '')
        
        # تنظيف نتائج الاستيراد من الجلسة لمنع ظهور النافذة تلقائيا
        if 'import_results' in session:
            session.pop('import_results', None)
        
        query = Employee.query.filter_by(is_directorate_employee=True)
        
        if search_term:
            query = query.filter(
                (Employee.name.contains(search_term)) |
                (Employee.ministry_number.contains(search_term)) |
                (Employee.civil_id.contains(search_term))
            )
        
        if job_filter:
            query = query.filter(Employee.job_title == job_filter)
        
        if school_filter:
            query = query.filter(Employee.school_id == school_filter)
        
        employees = query.all()
        
        # الحصول على أقسام المديرية والوظائف
        from constants import DIRECTORATE_DEPARTMENTS, DIRECTORATE_JOB_TITLES
        directorate_schools = School.query.filter(School.name.in_(DIRECTORATE_DEPARTMENTS)).order_by(School.name).all()
        
        return render_template('directorate_employees.html', 
                            employees=employees,
                            search_term=search_term,
                            schools=directorate_schools,
                            job_titles=DIRECTORATE_JOB_TITLES,
                            selected_job=job_filter,
                            selected_school=school_filter)
    except Exception as e:
        # Log the error
        print(f"Error in directorate_employees route: {str(e)}")
        flash(f"حدث خطأ أثناء تحميل صفحة موظفي المديرية: {str(e)}", "danger")
        return redirect(url_for('main.index'))

# إضافة موظف مديرية جديد
@employee.route('/directorate_employees/add', methods=['GET', 'POST'])
@permission_required('can_manage_employees')
def add_directorate_employee():
    from constants import DIRECTORATE_DEPARTMENTS
    
    if request.method == 'POST':
        # استخراج البيانات من النموذج
        name = request.form.get('name')
        civil_id = request.form.get('civil_id')
        ministry_number = request.form.get('ministry_number')
        job_title = request.form.get('job_title')
        school_id = request.form.get('school_id')
        phone_number = request.form.get('phone_number')
        gender = request.form.get('gender')
        qualification = request.form.get('qualification')
        appointment_date = request.form.get('appointment_date')
        
        # التحقق من الحقول المطلوبة
        if not all([name, civil_id, ministry_number, job_title, school_id, gender, qualification, appointment_date]):
            flash('جميع الحقول المطلوبة يجب أن تكون مملوءة', 'danger')
            from constants import DIRECTORATE_DEPARTMENTS
            departments = School.query.filter(School.name.in_(DIRECTORATE_DEPARTMENTS)).order_by(School.name).all()
            return render_template('employee_form.html', employee=None, schools=departments, job_titles=DIRECTORATE_JOB_TITLES, is_directorate=True)
        
        # التحقق من عدم وجود موظف بنفس الرقم المدني
        existing_employee = Employee.query.filter_by(civil_id=civil_id).first()
        if existing_employee:
            flash('يوجد موظف بنفس الرقم المدني', 'danger')
            from constants import DIRECTORATE_DEPARTMENTS
            departments = School.query.filter(School.name.in_(DIRECTORATE_DEPARTMENTS)).order_by(School.name).all()
            return render_template('employee_form.html', employee=None, schools=departments, job_titles=DIRECTORATE_JOB_TITLES, is_directorate=True)
        else:
            # تحويل تاريخ التعيين من نص إلى تاريخ
            try:
                appointment_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
            except ValueError:
                flash('تاريخ التعيين غير صحيح', 'danger')
                from constants import DIRECTORATE_DEPARTMENTS
                departments = School.query.filter(School.name.in_(DIRECTORATE_DEPARTMENTS)).order_by(School.name).all()
                return render_template('employee_form.html', employee=None, schools=departments, job_titles=DIRECTORATE_JOB_TITLES, is_directorate=True)
            
            # إنشاء موظف مديرية جديد
            # إضافة رصيد الإجازات لموظفي المديرية
   
            
            # التحقق من أن القسم المختار من أقسام المديرية
            selected_school = School.query.get(int(school_id))
            is_directorate = selected_school.name in DIRECTORATE_DEPARTMENTS if selected_school else False
            
            # إنشاء موظف مديرية جديد
            employee = Employee(
                name=name,
                civil_id=civil_id,
                ministry_number=ministry_number,
                job_title=job_title,
                school_id=int(school_id),
                phone_number=phone_number,
                gender=gender,
                qualification=qualification,
                appointment_date=appointment_date,
                is_directorate_employee=is_directorate,  # تحديد أنه موظف مديرية
                # تعيين الرصيد المدخل يدوياً
               
            )
            db.session.add(employee)
            db.session.commit()
            flash('تمت إضافة موظف المديرية بنجاح', 'success')
            return redirect(url_for('employee.directorate_employees'))
    
    # الحصول على قائمة الأقسام فقط (أقسام المديرية)
    from constants import DIRECTORATE_DEPARTMENTS
    departments = School.query.filter(School.name.in_(DIRECTORATE_DEPARTMENTS)).order_by(School.name).all()
    
    return render_template('employee_form.html', employee=None, schools=departments, job_titles=DIRECTORATE_JOB_TITLES, is_directorate=True)

# API للبحث عن الموظفين
@employee.route('/api/employee/search_by_name_or_number')
def search_by_name_or_number():
    search_term = request.args.get('search_term', '').strip()
    
    if not search_term:
        return jsonify({
            'success': False,
            'message': 'يرجى إدخال كلمة البحث'
        })
    
    # البحث في اسم الموظف أو الرقم الوزاري
    # تقييد البحث على موظفي المديرية فقط
    employees = Employee.query.filter(
        Employee.is_directorate_employee == True
    ).filter(
        (Employee.name.ilike(f'%{search_term}%')) |
        (Employee.ministry_number.ilike(f'%{search_term}%'))
    ).order_by(Employee.name).all()
    
    # تحويل النتائج إلى قاموس
    employee_list = []
    for emp in employees:
        employee_list.append({
            'id': emp.id,
            'name': emp.name,
            'ministry_number': emp.ministry_number,
            'school_name': emp.school.name if emp.school else ''
        })
    
    return jsonify({
        'success': True,
        'employees': employee_list
    })

# إضافة هذا الكود بعد السطر 413 (في نهاية الملف)

# API للبحث عن موظف بالرقم الوزاري (لصفحة النقل)
@employee.route('/api/employee/search')
def search_employee():
    ministry_number = request.args.get('ministry_number', '').strip()
    
    if not ministry_number:
        return jsonify({
            'success': False,
            'message': 'يرجى إدخال الرقم الوزاري'
        })
    
    # البحث عن الموظف بجزء من الرقم الوزاري (جميع الموظفين)
    employee = Employee.query.filter(
        Employee.ministry_number.ilike(f'%{ministry_number}%')
    ).first()
    
    if employee:
        return jsonify({
            'success': True,
            'employee': {
                'id': employee.id,
                'name': employee.name,
                'ministry_number': employee.ministry_number,
                'school_id': employee.school_id,
                'job_title': employee.job_title,
                'school_name': employee.school.name if employee.school else ''
            }
        })
    else:
        return jsonify({
            'success': False,
            'message': 'لم يتم العثور على موظف بهذا الرقم الوزاري'
        })

# عرض بيانات موظف مديرية
@employee.route('/directorate_employees/view/<int:id>')
def view_directorate_employee(id):
    employee = Employee.query.get_or_404(id)
    
    # التأكد من أن الموظف هو موظف مديرية
    if not employee.is_directorate_employee:
        flash('هذا الموظف ليس موظف مديرية', 'warning')
        return redirect(url_for('employee.directorate_employees'))
    
    return render_template('directorate_employee_view.html', employee=employee)

# تعديل بيانات موظف مديرية
@employee.route('/directorate_employees/edit/<int:id>', methods=['GET', 'POST'])
@permission_required('can_manage_employees')
def edit_directorate_employee(id):
    from constants import DIRECTORATE_DEPARTMENTS, DIRECTORATE_JOB_TITLES
    
    employee = Employee.query.get_or_404(id)
    
    # التأكد من أن الموظف هو موظف مديرية
    if not employee.is_directorate_employee:
        flash('هذا الموظف ليس موظف مديرية', 'warning')
        return redirect(url_for('employee.directorate_employees'))
    
    if request.method == 'POST':
        # استخراج البيانات من النموذج
        name = request.form.get('name')
        civil_id = request.form.get('civil_id')
        ministry_number = request.form.get('ministry_number')
        job_title = request.form.get('job_title')
        school_id = request.form.get('school_id')
        phone_number = request.form.get('phone_number')
        gender = request.form.get('gender')
        qualification = request.form.get('qualification')
        appointment_date = request.form.get('appointment_date')
        bachelor_specialization = request.form.get('bachelor_specialization')
        high_diploma_specialization = request.form.get('high_diploma_specialization')
        masters_specialization = request.form.get('masters_specialization')
        phd_specialization = request.form.get('phd_specialization')
        
        # التحقق من الحقول المطلوبة
        if not all([name, civil_id, ministry_number, job_title, school_id, gender, qualification]):
            flash('جميع الحقول المطلوبة يجب أن تكون مملوءة', 'danger')
            departments = School.query.filter(School.name.in_(DIRECTORATE_DEPARTMENTS)).order_by(School.name).all()
            return render_template('employee_form.html', employee=employee, schools=departments, job_titles=DIRECTORATE_JOB_TITLES, is_directorate=True)
        
        # التحقق من عدم وجود موظف آخر بنفس الرقم المدني
        existing_employee = Employee.query.filter(Employee.civil_id == civil_id, Employee.id != employee.id).first()
        if existing_employee:
            flash('يوجد موظف آخر بنفس الرقم المدني', 'danger')
            departments = School.query.filter(School.name.in_(DIRECTORATE_DEPARTMENTS)).order_by(School.name).all()
            return render_template('employee_form.html', employee=employee, schools=departments, job_titles=DIRECTORATE_JOB_TITLES, is_directorate=True)
        
        # تحويل تاريخ التعيين من نص إلى تاريخ
        try:
            if appointment_date:
                appointment_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
        except ValueError:
            flash('تاريخ التعيين غير صحيح', 'danger')
            departments = School.query.filter(School.name.in_(DIRECTORATE_DEPARTMENTS)).order_by(School.name).all()
            return render_template('employee_form.html', employee=employee, schools=departments, job_titles=DIRECTORATE_JOB_TITLES, is_directorate=True)
        
        # التحقق من أن القسم المختار من أقسام المديرية
        selected_school = School.query.get(int(school_id))
        is_directorate = selected_school.name in DIRECTORATE_DEPARTMENTS if selected_school else False
        
        if not is_directorate:
            flash('يجب اختيار قسم من أقسام المديرية', 'danger')
            departments = School.query.filter(School.name.in_(DIRECTORATE_DEPARTMENTS)).order_by(School.name).all()
            return render_template('employee_form.html', employee=employee, schools=departments, job_titles=DIRECTORATE_JOB_TITLES, is_directorate=True)
        
        # تحديث بيانات الموظف
        employee.name = name
        employee.civil_id = civil_id
        employee.ministry_number = ministry_number
        employee.job_title = job_title
        employee.school_id = int(school_id)
        employee.phone_number = phone_number
        employee.gender = gender
        employee.qualification = qualification
        employee.bachelor_specialization = bachelor_specialization
        employee.high_diploma_specialization = high_diploma_specialization
        employee.masters_specialization = masters_specialization
        employee.phd_specialization = phd_specialization
        
        if appointment_date:
            employee.appointment_date = appointment_date
        
        db.session.commit()
        flash('تم تحديث بيانات الموظف بنجاح', 'success')
        return redirect(url_for('employee.directorate_employees'))
    
    # الحصول على أقسام المديرية
    departments = School.query.filter(School.name.in_(DIRECTORATE_DEPARTMENTS)).order_by(School.name).all()
    
    return render_template('employee_form.html', employee=employee, schools=departments, job_titles=DIRECTORATE_JOB_TITLES, is_directorate=True)

# حذف موظف مديرية
@employee.route('/directorate_employees/delete/<int:id>', methods=['POST'])
@permission_required('can_delete_employee')
def delete_directorate_employee(id):
    employee = Employee.query.get_or_404(id)
    
    # التأكد من أن الموظف هو موظف مديرية
    if not employee.is_directorate_employee:
        flash('هذا الموظف ليس موظف مديرية', 'warning')
        return redirect(url_for('employee.directorate_employees'))
    
    try:
        # تسجيل نشاط الحذف
        log_user_activity(f'حذف موظف المديرية: {employee.name} - {employee.ministry_number}')
        
        # حذف الموظف
        db.session.delete(employee)
        db.session.commit()
        flash('تم حذف موظف المديرية بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء حذف الموظف: {str(e)}', 'danger')
    
    return redirect(url_for('employee.directorate_employees'))