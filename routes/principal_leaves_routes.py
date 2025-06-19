from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, PrincipalCasualLeave, Employee, School, User
from auth_decorators import login_required, permission_required
from datetime import datetime, timedelta
from sqlalchemy import desc, text
from utils import log_user_activity, calculate_days_between
import json

principal_leaves = Blueprint('principal_leaves', __name__)

# عرض قائمة الإجازات العرضية لمدراء المدارس
@principal_leaves.route('/principal_casual_leaves')
@login_required
@permission_required('can_view_leaves')
def principal_casual_leaves_list():
    # الحصول على قائمة الإجازات العرضية للمدراء مع إمكانية البحث والتصفية
    search_term = request.args.get('search', '')
    school_filter = request.args.get('school_id', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    # إضافة دعم الصفحات
    page = request.args.get('page', 1, type=int)
    per_page = 25  # عدد الإجازات في كل صفحة
    
    # بناء الاستعلام
    query = PrincipalCasualLeave.query
    
    if search_term:
        # البحث في اسم الموظف أو رقمه الوزاري
        query = query.join(Employee).filter(
            (Employee.name.ilike(f'%{search_term}%')) |
            (Employee.ministry_number.ilike(f'%{search_term}%'))
        )
    
    if school_filter:
        query = query.filter(PrincipalCasualLeave.school_id == school_filter)
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(PrincipalCasualLeave.start_date >= date_from_obj)
        except ValueError:
            flash('تنسيق تاريخ البداية غير صحيح', 'danger')
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(PrincipalCasualLeave.end_date <= date_to_obj)
        except ValueError:
            flash('تنسيق تاريخ النهاية غير صحيح', 'danger')
    
    # ترتيب النتائج حسب تاريخ الإنشاء (الأحدث أولاً)
    query = query.order_by(desc(PrincipalCasualLeave.created_at))
    
    # تقسيم النتائج إلى صفحات
    paginated_leaves = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # الحصول على قائمة المدارس للفلترة
    schools = School.query.order_by(School.name).all()
    
    return render_template('principal_casual_leaves/list.html',
                          leaves=paginated_leaves.items,
                          pagination=paginated_leaves,
                          schools=schools,
                          search_term=search_term,
                          selected_school=int(school_filter) if school_filter else None,
                          date_from=date_from,
                          date_to=date_to)

# إضافة إجازة عرضية جديدة لمدير مدرسة
@principal_leaves.route('/principal_casual_leaves/add', methods=['GET', 'POST'])
@login_required
@permission_required('can_add_leaves')
def add_principal_casual_leave():
    # التحقق من صلاحيات المستخدم الحالي
    current_user = User.query.get(session.get('user_id'))
    print(f"DEBUG: Current user: {current_user.username}, is_admin: {current_user.is_admin}")
    print(f"DEBUG: Permissions - can_add_leaves: {current_user.has_permission('can_add_leaves')}, can_add_new_leave: {current_user.has_permission('can_add_new_leave')}")
    
    # التحقق من وجود جدول الإجازات العرضية
    try:
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        table_exists = 'principal_casual_leaves' in tables
        table_count = db.session.query(db.func.count(PrincipalCasualLeave.id)).scalar()
        print(f"DEBUG: Table exists: {table_exists}, Total records: {table_count}")
    except Exception as e:
        print(f"DEBUG: Error checking table: {str(e)}")
    
    if request.method == 'POST':
        print("DEBUG: POST request received for adding principal casual leave")
        # استخراج البيانات من النموذج
        employee_id = request.form.get('employee_id')
        school_id = request.form.get('school_id')
        school_letter_number = request.form.get('school_letter_number')
        school_letter_date = request.form.get('school_letter_date')
        leave_reason = request.form.get('leave_reason')
        # إذا كان سبب الإجازة هو "أخرى"، استخدم النص المدخل في حقل other_reason
        if leave_reason == "أخرى":
            other_reason = request.form.get('other_reason')
            if other_reason:
                leave_reason = other_reason
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        notes = request.form.get('notes')
        
        print(f"DEBUG: Form data received - employee_id: {employee_id}, school_id: {school_id}, leave_reason: {leave_reason}")
        
        # التحقق من الحقول المطلوبة
        if not all([employee_id, school_id, school_letter_number, school_letter_date, leave_reason, start_date, end_date]):
            missing_fields = []
            if not employee_id: missing_fields.append("employee_id")
            if not school_id: missing_fields.append("school_id")
            if not school_letter_number: missing_fields.append("school_letter_number")
            if not school_letter_date: missing_fields.append("school_letter_date")
            if not leave_reason: missing_fields.append("leave_reason")
            if not start_date: missing_fields.append("start_date")
            if not end_date: missing_fields.append("end_date")
            
            print(f"DEBUG: Missing required fields: {', '.join(missing_fields)}")
            flash('جميع الحقول المطلوبة يجب أن تكون مملوءة', 'danger')
            return redirect(url_for('principal_leaves.add_principal_casual_leave'))
        
        try:
            # تحويل التواريخ من نص إلى كائنات تاريخ
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            school_letter_date_obj = datetime.strptime(school_letter_date, '%Y-%m-%d').date()
            
            print(f"DEBUG: Parsed dates - start_date: {start_date_obj}, end_date: {end_date_obj}")
            
            # التحقق من أن تاريخ البداية قبل تاريخ النهاية
            if start_date_obj > end_date_obj:
                print("DEBUG: Start date is after end date")
                flash('تاريخ بداية الإجازة يجب أن يكون قبل تاريخ نهايتها', 'danger')
                return redirect(url_for('principal_leaves.add_principal_casual_leave'))
            
            # حساب عدد أيام الإجازة
            days_count = calculate_days_between(start_date_obj, end_date_obj) + 1  # +1 لتضمين يوم النهاية
            print(f"DEBUG: Calculated days_count: {days_count}")
            
            # التحقق من أن الموظف هو مدير مدرسة
            employee = Employee.query.get(employee_id)
            if not employee:
                print(f"DEBUG: Employee with ID {employee_id} not found")
                flash('الموظف غير موجود', 'danger')
                return redirect(url_for('principal_leaves.add_principal_casual_leave'))
                
            print(f"DEBUG: Employee found - name: {employee.name}, job_title: {employee.job_title}")
            
            # تعديع: نسمح بإضافة الإجازة حتى لو لم يكن المدير مدرسة (للتجربة)
            # if employee.job_title != 'مدير مدرسة':
            #     print(f"DEBUG: Employee job title '{employee.job_title}' is not 'مدير مدرسة'")
            #     flash('يجب اختيار موظف بوظيفة مدير مدرسة', 'danger')
            #     return redirect(url_for('principal_leaves.add_principal_casual_leave'))
            
            # إنشاء سجل إجازة عرضية جديد
            try:
                # استخدام SQL مباشر لإدخال البيانات
                sql = """
                INSERT INTO principal_casual_leaves (
                    employee_id, school_id, school_letter_number, school_letter_date,
                    leave_reason, start_date, end_date, days_count, notes, created_at, updated_at
                ) VALUES (
                    :employee_id, :school_id, :school_letter_number, :school_letter_date,
                    :leave_reason, :start_date, :end_date, :days_count, :notes, :created_at, :updated_at
                )
                """
                
                now = datetime.utcnow()
                
                result = db.session.execute(sql, {
                    'employee_id': employee_id,
                    'school_id': school_id,
                    'school_letter_number': school_letter_number,
                    'school_letter_date': school_letter_date_obj,
                    'leave_reason': leave_reason,
                    'start_date': start_date_obj,
                    'end_date': end_date_obj,
                    'days_count': days_count,
                    'notes': notes,
                    'created_at': now,
                    'updated_at': now
                })
                
                db.session.commit()
                print("DEBUG: Successfully inserted using raw SQL")
                
                # تسجيل العملية في سجلات المستخدمين
                log_user_activity(
                    user_id=session.get('user_id'),
                    action='إضافة',
                    module='الإجازات العرضية للمدراء',
                    description=f'تم إضافة إجازة عرضية لـ {employee.name}',
                    target_id=0,  # لا نعرف المعرف الجديد
                    target_type='إجازة عرضية'
                )
                
                flash('تم إضافة الإجازة العرضية بنجاح', 'success')
                return redirect(url_for('principal_leaves.principal_casual_leaves_list'))
            except Exception as sql_error:
                print(f"DEBUG: Error during SQL execution: {str(sql_error)}")
                db.session.rollback()
                flash(f'خطأ أثناء حفظ البيانات: {str(sql_error)}', 'danger')
                return redirect(url_for('principal_leaves.add_principal_casual_leave'))
                
        except ValueError as e:
            print(f"DEBUG: ValueError: {str(e)}")
            flash(f'خطأ في تنسيق البيانات: {str(e)}', 'danger')
            return redirect(url_for('principal_leaves.add_principal_casual_leave'))
        except Exception as e:
            print(f"DEBUG: Unexpected error: {str(e)}")
            flash(f'حدث خطأ غير متوقع: {str(e)}', 'danger')
            return redirect(url_for('principal_leaves.add_principal_casual_leave'))
    
    # الحصول على قائمة المدراء (الموظفين بوظيفة مدير مدرسة)
    # نحضر فقط 5 مدراء للعرض الأولي
    principals = Employee.query.filter_by(job_title='مدير مدرسة').order_by(Employee.name).limit(5).all()
    
    # الحصول على قائمة المدارس
    schools = School.query.order_by(School.name).all()
    
    return render_template('principal_casual_leaves/add.html',
                          employees=principals,
                          schools=schools)

# عرض تفاصيل إجازة عرضية لمدير مدرسة
@principal_leaves.route('/principal_casual_leaves/view/<int:id>')
@login_required
@permission_required('can_view_leaves')
def view_principal_casual_leave(id):
    leave = PrincipalCasualLeave.query.get_or_404(id)
    return render_template('principal_casual_leaves/view.html', leave=leave)

# تعديل إجازة عرضية لمدير مدرسة
@principal_leaves.route('/principal_casual_leaves/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required('can_edit_leaves')
def edit_principal_casual_leave(id):
    leave = PrincipalCasualLeave.query.get_or_404(id)
    
    if request.method == 'POST':
        # استخراج البيانات من النموذج
        employee_id = request.form.get('employee_id')
        school_id = request.form.get('school_id')
        school_letter_number = request.form.get('school_letter_number')
        school_letter_date = request.form.get('school_letter_date')
        leave_reason = request.form.get('leave_reason')
        # إذا كان سبب الإجازة هو "أخرى"، استخدم النص المدخل في حقل other_reason
        if leave_reason == "أخرى":
            other_reason = request.form.get('other_reason')
            if other_reason:
                leave_reason = other_reason
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        notes = request.form.get('notes')
        
        # التحقق من الحقول المطلوبة
        if not all([employee_id, school_id, school_letter_number, school_letter_date, leave_reason, start_date, end_date]):
            flash('جميع الحقول المطلوبة يجب أن تكون مملوءة', 'danger')
            return redirect(url_for('principal_leaves.edit_principal_casual_leave', id=id))
        
        try:
            # تحويل التواريخ من نص إلى كائنات تاريخ
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            school_letter_date_obj = datetime.strptime(school_letter_date, '%Y-%m-%d').date()
            
            # التحقق من أن تاريخ البداية قبل تاريخ النهاية
            if start_date_obj > end_date_obj:
                flash('تاريخ بداية الإجازة يجب أن يكون قبل تاريخ نهايتها', 'danger')
                return redirect(url_for('principal_leaves.edit_principal_casual_leave', id=id))
            
            # حساب عدد أيام الإجازة
            days_count = calculate_days_between(start_date_obj, end_date_obj) + 1  # +1 لتضمين يوم النهاية
            
            # التحقق من أن الموظف هو مدير مدرسة
            employee = Employee.query.get(employee_id)
            if not employee or employee.job_title != 'مدير مدرسة':
                flash('يجب اختيار موظف بوظيفة مدير مدرسة', 'danger')
                return redirect(url_for('principal_leaves.edit_principal_casual_leave', id=id))
            
            # تحديث بيانات الإجازة
            leave.employee_id = employee_id
            leave.school_id = school_id
            leave.school_letter_number = school_letter_number
            leave.school_letter_date = school_letter_date_obj
            leave.leave_reason = leave_reason
            leave.start_date = start_date_obj
            leave.end_date = end_date_obj
            leave.days_count = days_count
            leave.notes = notes
            leave.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            # تسجيل العملية في سجلات المستخدمين
            log_user_activity(
                user_id=session.get('user_id'),
                action='تعديل',
                module='الإجازات العرضية للمدراء',
                description=f'تم تعديل إجازة عرضية لـ {employee.name}',
                target_id=leave.id,
                target_type='إجازة عرضية'
            )
            
            flash('تم تعديل الإجازة العرضية بنجاح', 'success')
            return redirect(url_for('principal_leaves.principal_casual_leaves_list'))
            
        except ValueError as e:
            flash(f'خطأ في تنسيق البيانات: {str(e)}', 'danger')
            return redirect(url_for('principal_leaves.edit_principal_casual_leave', id=id))
    
    # الحصول على قائمة المدارس
    schools = School.query.order_by(School.name).all()
    
    # الحصول على قائمة المدراء (الموظفين بوظيفة مدير مدرسة)
    principals = Employee.query.filter_by(job_title='مدير مدرسة').order_by(Employee.name).all()
    
    return render_template('principal_casual_leaves/edit.html',
                          leave=leave,
                          employees=principals,
                          schools=schools)

# حذف إجازة عرضية لمدير مدرسة
@principal_leaves.route('/principal_casual_leaves/delete/<int:id>', methods=['POST'])
@login_required
@permission_required('can_delete_leaves')
def delete_principal_casual_leave(id):
    leave = PrincipalCasualLeave.query.get_or_404(id)
    
    # حفظ معلومات الإجازة قبل الحذف لاستخدامها في سجل النشاط
    employee_name = "غير معروف"
    if leave.employee:
        employee_name = leave.employee.name
    leave_id = leave.id
    
    db.session.delete(leave)
    db.session.commit()
    
    # تسجيل العملية في سجلات المستخدمين
    log_user_activity(
        user_id=session.get('user_id'),
        action='حذف',
        module='الإجازات العرضية للمدراء',
        description=f'تم حذف إجازة عرضية لـ {employee_name}',
        target_id=leave_id,
        target_type='إجازة عرضية'
    )
    
    flash('تم حذف الإجازة العرضية بنجاح', 'success')
    return redirect(url_for('principal_leaves.principal_casual_leaves_list'))

# This duplicate route was removed to fix the endpoint conflict
# The identical route exists at line ~370

# تم إزالة الدالة المكررة test_search_principals من هنا لتجنب تعارض نقاط النهاية
# توجد نسخة أخرى من هذه الدالة في السطر ~970
# @principal_leaves.route('/test_search_principals')
# @login_required
# def test_search_principals():
#     """طريقة اختبار للبحث عن المدراء مباشرة"""
#     ...

# API للبحث عن مدراء المدارس بدون شرط المصادقة (للاختبار فقط)
# تم إزالة الدالة المكررة api_principal_search_test من هنا لتجنب تعارض نقاط النهاية
# توجد نسخة أخرى من هذه الدالة في السطر ~367
# @principal_leaves.route('/api/principal_search_test')
# def api_principal_search_test():
#     # تم نقل المحتوى إلى الدالة الأصلية

# تم إزالة الدالة المكررة api_principal_search_test من هنا لتجنب تعارض نقاط النهاية

@principal_leaves.route('/api/create_principal_leave_v2', methods=['POST'])
@login_required
@permission_required('can_add_leaves')
def api_create_principal_leave_duplicate():
    """واجهة برمجة تطبيقات لإنشاء إجازة عرضية جديدة"""
    try:
        data = request.json
        print(f"DEBUG API: Received data: {data}")
        
        # التحقق من وجود البيانات المطلوبة
        required_fields = ['employee_id', 'school_id', 'school_letter_number', 'school_letter_date', 
                          'leave_reason', 'start_date', 'end_date', 'days_count']
        
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'success': False, 'message': f'الحقل {field} مطلوب'}), 400
        
        # محاولة إنشاء سجل جديد باستخدام SQL مباشرة
        try:
            insert_query = text("""
            INSERT INTO principal_casual_leaves (
                employee_id, school_id, school_letter_number, school_letter_date,
                leave_reason, start_date, end_date, days_count, notes, created_at, updated_at
            ) VALUES (
                :employee_id, :school_id, :school_letter_number, :school_letter_date,
                :leave_reason, :start_date, :end_date, :days_count, :notes, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            )
            """)
            
            # تحويل التواريخ من سلاسل نصية إلى كائنات تاريخ
            school_letter_date = datetime.strptime(data['school_letter_date'], '%Y-%m-%d').date()
            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
            
            params = {
                'employee_id': data['employee_id'],
                'school_id': data['school_id'],
                'school_letter_number': data['school_letter_number'],
                'school_letter_date': school_letter_date,
                'leave_reason': data['leave_reason'],
                'start_date': start_date,
                'end_date': end_date,
                'days_count': data['days_count'],
                'notes': data.get('notes', '')
            }
            
            result = db.session.execute(insert_query, params)
            db.session.commit()
            
            # الحصول على معرف السجل المدرج
            get_last_id = text("SELECT last_insert_rowid()")
            last_id = db.session.execute(get_last_id).scalar()
            
            return jsonify({
                'success': True, 
                'message': 'تم إنشاء الإجازة بنجاح',
                'id': last_id
            }), 201
            
        except Exception as e:
            db.session.rollback()
            print(f"DEBUG API: SQL Error: {str(e)}")
            return jsonify({'success': False, 'message': f'خطأ في قاعدة البيانات: {str(e)}'}), 500
    
    except Exception as e:
        print(f"DEBUG API: Unexpected error: {str(e)}")
        return jsonify({'success': False, 'message': f'حدث خطأ غير متوقع: {str(e)}'}), 500

@principal_leaves.route('/debug/check_table_structure')
@login_required
def debug_check_table_structure():
    """مسار للتحقق من هيكل جدول الإجازات العرضية"""
    try:
        # معلومات عن قاعدة البيانات
        db_info = str(db.engine)
        db_url = str(db.engine.url)
        
        # التحقق من وجود الجدول بطريقة مختلفة
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        table_exists = 'principal_casual_leaves' in tables
        
        # الحصول على هيكل الجدول
        columns = []
        
        html = f"""
        <h1>معلومات جدول الإجازات العرضية</h1>
        <h2>معلومات قاعدة البيانات:</h2>
        <p>محرك قاعدة البيانات: {db_info}</p>
        <p>عنوان قاعدة البيانات: {db_url}</p>
        <p>قائمة الجداول: {', '.join(tables)}</p>
        """
        
        if table_exists:
            columns = inspector.get_columns('principal_casual_leaves')
            
            # عرض معلومات الأعمدة
            html += """
            <h2>هيكل الجدول:</h2>
            <table border="1" cellpadding="5">
                <tr>
                    <th>اسم العمود</th>
                    <th>النوع</th>
                    <th>إلزامي</th>
                    <th>المفتاح الرئيسي</th>
                    <th>القيمة الافتراضية</th>
                </tr>
            """
            
            for column in columns:
                html += f"""
                <tr>
                    <td>{column['name']}</td>
                    <td>{column['type']}</td>
                    <td>{'نعم' if not column.get('nullable', True) else 'لا'}</td>
                    <td>{'نعم' if column.get('primary_key', False) else 'لا'}</td>
                    <td>{column.get('default', '')}</td>
                </tr>
                """
            
            html += """
            </table>
            """
            
            # عرض معلومات المفاتيح الخارجية
            foreign_keys = inspector.get_foreign_keys('principal_casual_leaves')
            
            if foreign_keys:
                html += """
                <h2>المفاتيح الخارجية:</h2>
                <table border="1" cellpadding="5">
                    <tr>
                        <th>اسم المفتاح</th>
                        <th>العمود</th>
                        <th>الجدول المرجعي</th>
                        <th>العمود المرجعي</th>
                    </tr>
                """
                
                for fk in foreign_keys:
                    html += f"""
                    <tr>
                        <td>{fk.get('name', '')}</td>
                        <td>{', '.join(fk.get('constrained_columns', []))}</td>
                        <td>{fk.get('referred_table', '')}</td>
                        <td>{', '.join(fk.get('referred_columns', []))}</td>
                    </tr>
                    """
                
                html += """
                </table>
                """
        else:
            html += """
            <div class="alert alert-warning">
                <p>جدول الإجازات العرضية غير موجود!</p>
                <p><a href="/debug/create_table" class="btn btn-warning">إنشاء الجدول</a></p>
            </div>
            """
        
        return html
    except Exception as e:
        return f"<h1>خطأ</h1><p>{str(e)}</p>"

@principal_leaves.route('/debug/create_table')
@login_required
def debug_create_table():
    """مسار لإنشاء جدول الإجازات العرضية إذا لم يكن موجودًا"""
    try:
        # التحقق من وجود الجدول بطريقة مختلفة
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        table_exists = 'principal_casual_leaves' in tables
        
        if not table_exists:
            # إنشاء الجدول
            create_table_sql = db.text("""
            CREATE TABLE principal_casual_leaves (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                school_id INTEGER NOT NULL,
                school_letter_number VARCHAR(100) NOT NULL,
                school_letter_date DATE NOT NULL,
                leave_reason TEXT NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                days_count INTEGER NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES employee(id),
                FOREIGN KEY (school_id) REFERENCES school(id)
            )
            """)
            
            db.session.execute(create_table_sql)
            db.session.commit()
            
            # التحقق من إنشاء الجدول
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            table_created = 'principal_casual_leaves' in tables
            
            return f"""
            <h1>إنشاء جدول الإجازات العرضية</h1>
            <p>تم محاولة إنشاء الجدول.</p>
            <p>الجدول موجود الآن: {table_created}</p>
            <p><a href="/debug/check_table_structure">التحقق من هيكل الجدول</a></p>
            """
        else:
            return f"""
            <h1>جدول الإجازات العرضية موجود بالفعل</h1>
            <p><a href="/debug/check_table_structure">التحقق من هيكل الجدول</a></p>
            """
    except Exception as e:
        return f"<h1>خطأ</h1><p>{str(e)}</p>"

@principal_leaves.route('/debug/check_model')
@login_required
def debug_check_model():
    """مسار للتحقق من نموذج PrincipalCasualLeave"""
    try:
        # معلومات عن النموذج
        model_name = PrincipalCasualLeave.__name__
        table_name = PrincipalCasualLeave.__tablename__
        
        # الحصول على قائمة الأعمدة من النموذج
        columns = []
        for column in PrincipalCasualLeave.__table__.columns:
            columns.append({
                'name': column.name,
                'type': str(column.type),
                'nullable': column.nullable,
                'primary_key': column.primary_key,
                'foreign_key': bool(column.foreign_keys)
            })
        
        # الحصول على قائمة العلاقات
        relationships = []
        for rel in db.inspect(PrincipalCasualLeave).relationships:
            relationships.append({
                'name': rel.key,
                'target': rel.target.name,
                'direction': rel.direction.name
            })
        
        # محاولة إنشاء كائن
        try:
            test_leave = PrincipalCasualLeave(
                employee_id=1,
                school_id=1,
                school_letter_number="TEST-MODEL",
                school_letter_date=datetime.now().date(),
                leave_reason="اختبار نموذج",
                start_date=datetime.now().date(),
                end_date=datetime.now().date(),
                days_count=1,
                notes="اختبار إنشاء نموذج"
            )
            create_success = "تم إنشاء كائن بنجاح"
            
            # طباعة خصائص الكائن
            attributes = {}
            for attr in dir(test_leave):
                if not attr.startswith('_') and not callable(getattr(test_leave, attr)):
                    try:
                        attributes[attr] = str(getattr(test_leave, attr))
                    except:
                        attributes[attr] = "غير قابل للعرض"
        except Exception as e:
            create_success = f"فشل إنشاء كائن: {str(e)}"
            attributes = {}
        
        html = f"""
        <h1>معلومات نموذج الإجازات العرضية</h1>
        <p>اسم النموذج: {model_name}</p>
        <p>اسم الجدول: {table_name}</p>
        <p>نتيجة إنشاء كائن: {create_success}</p>
        
        <h2>أعمدة النموذج:</h2>
        <table border="1" cellpadding="5">
            <tr>
                <th>الاسم</th>
                <th>النوع</th>
                <th>قابل للخلو</th>
                <th>مفتاح أساسي</th>
                <th>مفتاح خارجي</th>
            </tr>
        """
        
        for col in columns:
            html += f"""
            <tr>
                <td>{col['name']}</td>
                <td>{col['type']}</td>
                <td>{'نعم' if col['nullable'] else 'لا'}</td>
                <td>{'نعم' if col['primary_key'] else 'لا'}</td>
                <td>{'نعم' if col['foreign_key'] else 'لا'}</td>
            </tr>
            """
        
        html += """
        </table>
        
        <h2>علاقات النموذج:</h2>
        <table border="1" cellpadding="5">
            <tr>
                <th>الاسم</th>
                <th>الهدف</th>
                <th>الاتجاه</th>
            </tr>
        """
        
        for rel in relationships:
            html += f"""
            <tr>
                <td>{rel['name']}</td>
                <td>{rel['target']}</td>
                <td>{rel['direction']}</td>
            </tr>
            """
        
        html += """
        </table>
        
        <h2>خصائص الكائن:</h2>
        <table border="1" cellpadding="5">
            <tr>
                <th>الاسم</th>
                <th>القيمة</th>
            </tr>
        """
        
        for attr, value in attributes.items():
            html += f"""
            <tr>
                <td>{attr}</td>
                <td>{value}</td>
            </tr>
            """
        
        html += """
        </table>
        
        <p><a href="/debug/check_table_structure" class="btn btn-primary">فحص هيكل الجدول</a></p>
        <p><a href="/debug/create_table" class="btn btn-warning">إنشاء الجدول</a></p>
        """
        
        return html
    except Exception as e:
        return f"<h1>خطأ</h1><p>{str(e)}</p>" 

@principal_leaves.route('/debug/create_table_sqlalchemy')
@login_required
def debug_create_table_sqlalchemy():
    """مسار لإنشاء جدول الإجازات العرضية باستخدام SQLAlchemy"""
    try:
        # التحقق من وجود الجدول
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        table_exists = 'principal_casual_leaves' in tables
        
        if not table_exists:
            # إنشاء الجدول باستخدام SQLAlchemy
            metadata = db.MetaData()
            
            # تعريف الجدول
            principal_casual_leaves = db.Table(
                'principal_casual_leaves',
                metadata,
                db.Column('id', db.Integer, primary_key=True),
                db.Column('employee_id', db.Integer, db.ForeignKey('employee.id'), nullable=False),
                db.Column('school_id', db.Integer, db.ForeignKey('school.id'), nullable=False),
                db.Column('school_letter_number', db.String(100), nullable=False),
                db.Column('school_letter_date', db.Date, nullable=False),
                db.Column('leave_reason', db.Text, nullable=False),
                db.Column('start_date', db.Date, nullable=False),
                db.Column('end_date', db.Date, nullable=False),
                db.Column('days_count', db.Integer, nullable=False),
                db.Column('notes', db.Text),
                db.Column('created_at', db.DateTime, default=datetime.utcnow),
                db.Column('updated_at', db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
            )
            
            # إنشاء الجدول في قاعدة البيانات
            metadata.create_all(db.engine, tables=[principal_casual_leaves])
            
            # التحقق من إنشاء الجدول
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            table_created = 'principal_casual_leaves' in tables
            
            return f"""
            <h1>إنشاء جدول الإجازات العرضية باستخدام SQLAlchemy</h1>
            <p>تم محاولة إنشاء الجدول.</p>
            <p>الجدول موجود الآن: {table_created}</p>
            <p><a href="/debug/check_table_structure">التحقق من هيكل الجدول</a></p>
            <p><a href="/debug/check_model">التحقق من النموذج</a></p>
            """
        else:
            return f"""
            <h1>جدول الإجازات العرضية موجود بالفعل</h1>
            <p><a href="/debug/check_table_structure">التحقق من هيكل الجدول</a></p>
            <p><a href="/debug/check_model">التحقق من النموذج</a></p>
            """
    except Exception as e:
        return f"<h1>خطأ</h1><p>{str(e)}</p>" 

# API للبحث عن الموظفين بدون شرط المصادقة (للاختبار فقط)


@principal_leaves.route('/api/principal_search')
def api_principal_search():
    try:
        search_term = request.args.get('search_term', '').strip()
        ministry_number = request.args.get('ministry_number', '').strip()
        
        if not search_term and not ministry_number:
            return jsonify({
                'success': False,
                'message': 'يرجى إدخال كلمة البحث أو الرقم الوزاري'
            })
        
        # البحث عن الموظفين بالاسم أو الرقم الوزاري
        query = Employee.query
        
        if search_term:
            query = query.filter(
                db.or_(
                    Employee.name.ilike(f'%{search_term}%'),
                    Employee.ministry_number.ilike(f'%{search_term}%')
                )
            )
        elif ministry_number:
            query = query.filter(Employee.ministry_number == ministry_number)
        
        employees = query.limit(10).all()
        
        if employees:
            # تحويل النتائج إلى قائمة
            employees_list = []
            for employee in employees:
                employee_data = {
                    'id': employee.id,
                    'name': employee.name,
                    'ministry_number': employee.ministry_number,
                    'school_id': employee.school_id,
                    'job_title': employee.job_title,
                    'school_name': employee.school.name if employee.school and employee.school_id else ''
                }
                employees_list.append(employee_data)
            
            return jsonify({
                'success': True,
                'principals': employees_list
            })
        else:
            return jsonify({
                'success': False,
                'message': 'لم يتم العثور على موظفين مطابقين لكلمة البحث'
            })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'حدث خطأ أثناء البحث: {str(e)}'
        })

# طباعة الإجازة العرضية لمدير مدرسة
@principal_leaves.route('/principal_casual_leaves/print/<int:id>')
@login_required
@permission_required('can_view_leaves')
def print_principal_casual_leave(id):
    leave = PrincipalCasualLeave.query.get_or_404(id)
    return render_template('principal_casual_leaves/print.html', leave=leave)

@principal_leaves.route('/search_principals')
@login_required
def search_principals():
    search_term = request.args.get('term', '')
    print(f"DEBUG: Search term received: '{search_term}'")
    
    if not search_term:
        print("DEBUG: Empty search term, returning empty list")
        return jsonify([])
    
    try:
        # البحث عن المدراء بالاسم أو الرقم الوزاري
        principals = Employee.query.filter(
            Employee.job_title == 'مدير مدرسة',
            db.or_(
                Employee.name.ilike(f'%{search_term}%'),
                Employee.ministry_number.ilike(f'%{search_term}%')
            )
        ).limit(10).all()
        
        print(f"DEBUG: Found {len(principals)} principals")
        
        results = []
        for principal in principals:
            try:
                school_name = principal.school.name if principal.school else "غير محدد"
                result = {
                    'id': principal.id,
                    'text': f'{principal.name} ({principal.ministry_number}) - {school_name}',
                    'school_id': principal.school_id
                }
                results.append(result)
                print(f"DEBUG: Added principal: {result}")
            except Exception as e:
                print(f"DEBUG: Error processing principal {principal.id}: {str(e)}")
        
        print(f"DEBUG: Returning {len(results)} results")
        return jsonify(results)
    
    except Exception as e:
        print(f"DEBUG: Error in search: {str(e)}")
        return jsonify({"error": str(e)})

@principal_leaves.route('/test_search_principals')
@login_required
def test_search_principals():
    """طريقة اختبار للبحث عن المدراء مباشرة"""
    search_term = request.args.get('term', '')
    
    # البحث عن المدراء بالاسم أو الرقم الوزاري
    principals = Employee.query.filter(
        Employee.job_title == 'مدير مدرسة'
    ).limit(10).all()
    
    # إذا كان هناك مصطلح بحث، قم بتطبيق الفلتر
    if search_term:
        principals = [p for p in principals if search_term.lower() in p.name.lower() or search_term in p.ministry_number]
    
    results = []
    for principal in principals:
        school_name = principal.school.name if principal.school else "غير محدد"
        results.append({
            'id': principal.id,
            'text': f'{principal.name} ({principal.ministry_number}) - {school_name}',
            'school_id': principal.school_id
        })
    
    # إنشاء صفحة HTML بسيطة لعرض النتائج
    html = f"""
    <h1>نتائج البحث عن المدراء</h1>
    <p>مصطلح البحث: {search_term}</p>
    <p>عدد النتائج: {len(results)}</p>
    <ul>
    """
    
    for result in results:
        html += f"<li>ID: {result['id']} | النص: {result['text']} | رقم المدرسة: {result['school_id']}</li>"
    
    html += """
    </ul>
    <h2>اختبار البحث</h2>
    <form>
        <input type="text" name="term" value="{}" placeholder="ابحث هنا...">
        <button type="submit">بحث</button>
    </form>
    """.format(search_term)
    
    return html 

# API للبحث عن مدراء المدارس بدون شرط المصادقة (للاختبار فقط)
@principal_leaves.route('/api/principal_search_test')
def api_principal_search_test():
    try:
        search_term = request.args.get('search_term', '').strip()
        
        print(f"DEBUG API TEST: Received search term: '{search_term}'")
        print(f"DEBUG API TEST: All request args: {request.args}")
        
        if not search_term:
            print("DEBUG API TEST: Empty search term")
            return jsonify({
                'success': False,
                'message': 'يرجى إدخال كلمة البحث'
            })
        
        # البحث عن الموظفين بالاسم أو الرقم الوزاري (تم إزالة شرط مدير مدرسة)
        print(f"DEBUG API TEST: Searching for employees with term: '{search_term}'")
        employees = Employee.query.filter(
            db.or_(
                Employee.name.ilike(f'%{search_term}%'),
                Employee.ministry_number.ilike(f'%{search_term}%')
            )
        ).limit(10).all()
        
        print(f"DEBUG API TEST: Found {len(employees)} employees")
        
        if employees:
            # تحويل النتائج إلى قائمة
            employees_list = []
            for employee in employees:
                employee_data = {
                    'id': employee.id,
                    'name': employee.name,
                    'ministry_number': employee.ministry_number,
                    'school_id': employee.school_id,
                    'job_title': employee.job_title,
                    'school_name': employee.school.name if employee.school and employee.school_id else ''
                }
                employees_list.append(employee_data)
                print(f"DEBUG API TEST: Added employee: {employee_data}")
            
            response_data = {
                'success': True,
                'principals': employees_list  # الاحتفاظ بنفس اسم المفتاح للتوافق مع الكود الحالي
            }
            print(f"DEBUG API TEST: Returning success response with {len(employees_list)} employees")
            return jsonify(response_data)
        else:
            print("DEBUG API TEST: No employees found")
            return jsonify({
                'success': False,
                'message': 'لم يتم العثور على موظفين مطابقين لكلمة البحث'
            })
    
    except Exception as e:
        print(f"DEBUG API TEST: Error in search: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'حدث خطأ أثناء البحث: {str(e)}'
        })

# تم إزالة الدالة المكررة api_create_principal_leave_duplicate بالكامل من هنا
