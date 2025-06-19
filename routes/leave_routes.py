from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from database import db
from utils import log_user_activity
from models import Employee, Leave, School, ConvertedDeparture, LeaveBalance
from datetime import datetime, timedelta
from sqlalchemy import func
from routes.auth_routes import login_required, permission_required  # إضافة login_required هنا

leave = Blueprint('leave', __name__)

# صفحة الإجازات
# تحديث route leaves
@leave.route('/leaves')
def leaves():
    search_term = request.args.get('search', '')
    selected_department = request.args.get('department_id', '')
    selected_leave_type = request.args.get('leave_type', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    # بناء استعلام الإجازات - استبعاد المغادرات تماماً
    leaves_query = Leave.query.join(Employee).join(School).filter(
        Leave.leave_type != 'مغادرة'  # استبعاد جميع المغادرات
    )
    
    if search_term:
        leaves_query = leaves_query.filter(
            db.or_(
                Employee.name.contains(search_term),
                Employee.civil_id.contains(search_term),
                Employee.ministry_number.contains(search_term)
            )
        )
    
    if selected_department:
        leaves_query = leaves_query.filter(Employee.school_id == selected_department)
    
    if selected_leave_type:
        leaves_query = leaves_query.filter(Leave.leave_type == selected_leave_type)
    
    if start_date:
        leaves_query = leaves_query.filter(Leave.start_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    
    if end_date:
        leaves_query = leaves_query.filter(Leave.end_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    
    leaves = leaves_query.order_by(Leave.start_date.desc()).all()
    
    # عرض أقسام المديرية فقط في الفلترة
    from constants import DIRECTORATE_DEPARTMENTS
    departments = School.query.filter(School.name.in_(DIRECTORATE_DEPARTMENTS)).order_by(School.name).all()
    
    return render_template('leaves.html',
                         leaves=leaves,
                         departments=departments,
                         leave_types=LEAVE_TYPES,
                         search_term=search_term,
                         selected_department=int(selected_department) if selected_department else '',
                         selected_leave_type=selected_leave_type,
                         start_date=start_date,
                         end_date=end_date)



# صفحة المغادرات
@leave.route('/departures')
def departures():
    # الحصول على معايير التصفية
    employee_name = request.args.get('employee_name', '')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # بناء الاستعلام مع تقييد موظفي المديرية فقط
    query = Leave.query.join(Employee).filter(Employee.is_directorate_employee == True)
    
    # تطبيق التصفية حسب اسم الموظف
    if employee_name:
        query = query.filter(Employee.name.contains(employee_name))
    
    # تطبيق التصفية حسب تارية البداية
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        query = query.filter(Leave.start_date >= start_date)
    
    # تطبيق التصفية حسب تارية النهاية
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        query = query.filter(Leave.end_date <= end_date)
    
    # عرض المغادرات فقط
    query = query.filter(Leave.leave_type == 'مغادرة')
    
    departures = query.order_by(Leave.start_date.desc()).all()
    
    # حساب إجمالي الساعات
    total_hours = sum(departure.hours_count or 0 for departure in departures)
    
    # حساب أيام المغادرات (كل 7 ساعات = يوم إجازة)
    departure_days = int(total_hours // 7)
    remaining_hours = total_hours % 7
    
    return render_template('departures.html',
                         departures=departures,
                         total_hours=total_hours,
                         departure_days=departure_days,
                         remaining_hours=remaining_hours)

# إضافة مغادرة جديدة
@leave.route('/add_departure', methods=['GET', 'POST'])
@permission_required('can_manage_leaves')
def add_departure():
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        departure_date = datetime.strptime(request.form.get('departure_date'), '%Y-%m-%d').date()
        start_time = datetime.strptime(request.form.get('start_time'), '%H:%M').time()
        end_time = datetime.strptime(request.form.get('end_time'), '%H:%M').time()
        reason = request.form.get('reason')
        notes = request.form.get('notes')
        
        # حساب عدد الساعات
        start_datetime = datetime.combine(departure_date, start_time)
        end_datetime = datetime.combine(departure_date, end_time)
        
        # إذا كان وقت الانتهاء أقل من وقت البداية، فهذا يعني أن المغادرة تمتد لليوم التالي
        if end_time < start_time:
            end_datetime += timedelta(days=1)
        
        duration = end_datetime - start_datetime
        hours_count = duration.total_seconds() / 3600
        
        # إنشاء سجل المغادرة فقط (بدون تحويل مباشر)
        new_departure = Leave(
            employee_id=employee_id,
            leave_type='مغادرة',
            start_date=departure_date,
            end_date=departure_date,
            days_count=0,  # المغادرات لا تحسب كأيام إجازة مباشرة
            start_time=start_time,
            end_time=end_time,
            hours_count=hours_count,
            reason=reason,
            notes=notes
        )
        
        db.session.add(new_departure)
        db.session.commit()
        
        # تسجيل العملية في سجلات المستخدمين
        employee = Employee.query.get(employee_id)
        log_user_activity(
            user_id=session.get('user_id'),
            action='إضافة',
            module='المغادرات',
            description=f'تم إضافة مغادرة للموظف: {employee.name} في تاريخ {departure_date}',
            target_id=new_departure.id,
            target_type='مغادرة'
        )
        
        flash('تم إضافة المغادرة بنجاح', 'success')
        return redirect(url_for('leave.departures'))
    
    # الحصول على قائمة الموظفين للاختيار
    employees = Employee.query.filter_by(is_directorate_employee=True).order_by(Employee.name).all()
    
    return render_template('departure_form.html', employees=employees)


@leave.route('/departures_log')
def departures_log():
    # الحصول على معاملات الفلترة
    employee_id = request.args.get('employee_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # بناء الاستعلام للمغادرات فقط
    query = Leave.query.join(Employee).filter(
        Employee.is_directorate_employee == True,
        Leave.leave_type == 'مغادرة'  # المغادرات فقط
    )
    
    # تطبيق الفلاترة
    if employee_id:
        query = query.filter(Leave.employee_id == employee_id)
    
    if start_date:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        query = query.filter(Leave.start_date >= start_date_obj)
    
    if end_date:
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        query = query.filter(Leave.start_date <= end_date_obj)
    
    # ترتيب النتائج
    departures = query.order_by(Leave.start_date.desc()).all()
    
    # إعداد البيانات للعرض (بدون معلومات التحويل)
    departures_with_conversion = []
    for departure in departures:
        departures_with_conversion.append({
            'departure': departure,
            'converted_departure': None,  # لا توجد تحويلات
            'is_converted': False
        })
    
    # الحصول على قائمة الموظفين للفلترة
    employees = Employee.query.filter_by(is_directorate_employee=True).order_by(Employee.name).all()
    
    return render_template('departures_log.html', 
                         departures_with_conversion=departures_with_conversion,
                         employees=employees,
                         filters={
                             'employee_id': employee_id,
                             'start_date': start_date,
                             'end_date': end_date
                         })

@leave.route('/leaves/view/<int:id>')
def view_leave(id):
    leave_record = Leave.query.get_or_404(id)
    return render_template('leave_view.html', leave=leave_record)

# حذف مغادرة
# حذف مغادرة
@leave.route('/departures/delete/<int:id>', methods=['POST'])
@permission_required('can_manage_leaves')
def delete_departure(id):
    departure = Leave.query.get_or_404(id)
    
    # حفظ بيانات المغادرة قبل الحذف للتسجيل
    employee_name = departure.employee.name
    departure_date = departure.start_date
    departure_id = departure.id
    
    db.session.delete(departure)
    db.session.commit()
    
    # تسجيل العملية في سجلات المستخدمين
    log_user_activity(
        user_id=session.get('user_id'),
        action='حذف',
        module='المغادرات',
        description=f'تم حذف مغادرة الموظف: {employee_name} في تاريخ {departure_date}',
        target_id=departure_id,
        target_type='مغادرة'
    )
    
    flash('تم حذف المغادرة بنجاح', 'success')
    return redirect(url_for('leave.departures'))

# معالجة المغادرات الشهرية
# احذف هذه الدالة بالكامل أو علق عليها
# إضافة import في بداية الملف
from models import Employee, Leave, School, ConvertedDeparture, LeaveBalance, MonthlyDepartureBalance

# إضافة هذه الوظائف في نهاية الملف
@leave.route('/process_monthly_departures', methods=['GET', 'POST'])
@permission_required('can_manage_leaves')
def process_monthly_departures():
    if request.method == 'POST':
        month = int(request.form.get('month'))
        year = int(request.form.get('year'))
        
        # التحقق من أن الشهر لم يتم معالجته من قبل
        existing_processing = MonthlyDepartureBalance.query.filter_by(
            year=year, month=month, processed=True
        ).first()
        
        if existing_processing:
            flash(f'تم معالجة شهر {month}/{year} من قبل', 'warning')
            return redirect(url_for('leave.process_monthly_departures'))
        
        # تحديد بداية ونهاية الشهر
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        
        # الحصول على المغادرات في الشهر المحدد
        short_departures = Leave.query.filter(
            Leave.leave_type == 'مغادرة',
            Leave.start_date >= start_date.date(),
            Leave.start_date <= end_date.date(),
            Leave.hours_count <= 4  # المغادرات القصيرة فقط للاحتساب
        ).all()
        
        long_departures = Leave.query.filter(
            Leave.leave_type == 'مغادرة',
            Leave.start_date >= start_date.date(),
            Leave.start_date <= end_date.date(),
            Leave.hours_count > 4  # المغادرات الطويلة للترحيل المباشر
        ).all()
        
        # تجميع المغادرات حسب الموظف
        employee_short_departures = {}
        employee_long_departures = {}
        
        for dep in short_departures:
            if dep.employee_id not in employee_short_departures:
                employee_short_departures[dep.employee_id] = []
            employee_short_departures[dep.employee_id].append(dep)
        
        for dep in long_departures:
            if dep.employee_id not in employee_long_departures:
                employee_long_departures[dep.employee_id] = []
            employee_long_departures[dep.employee_id].append(dep)
        
        # معالجة المغادرات لكل موظف
        processed_employees = 0
        all_employee_ids = set(list(employee_short_departures.keys()) + list(employee_long_departures.keys()))
        
        for employee_id in all_employee_ids:
            # حساب إجمالي ساعات المغادرات القصيرة في الشهر الحالي
            short_deps = employee_short_departures.get(employee_id, [])
            current_month_hours = sum(dep.hours_count for dep in short_deps if dep.hours_count)
            
            # الحصول على الساعات المتبقية من الشهر السابق
            previous_month = month - 1 if month > 1 else 12
            previous_year = year if month > 1 else year - 1
            
            previous_balance = MonthlyDepartureBalance.query.filter_by(
                employee_id=employee_id,
                year=previous_year,
                month=previous_month
            ).first()
            
            carried_hours = previous_balance.remaining_hours if previous_balance else 0.0
            
            # حساب إجمالي الساعات (المتبقية من الشهر السابق + الشهر الحالي)
            total_hours = carried_hours + current_month_hours
            
            # حساب عدد الأيام الكاملة (كل 7 ساعات = يوم إجازة سنوية)
            days_to_convert = int(total_hours // 7)
            remaining_hours = total_hours % 7
            
            # معالجة المغادرات الطويلة (فوق 4 ساعات) - ترحيل مباشر
            long_deps = employee_long_departures.get(employee_id, [])
            long_departure_days = len(long_deps)  # كل مغادرة طويلة = يوم إجازة
            
            # إجمالي الأيام للتحويل
            total_days_to_convert = days_to_convert + long_departure_days
            
            # إنشاء سجل الرصيد الشهري
            monthly_balance = MonthlyDepartureBalance(
                employee_id=employee_id,
                year=year,
                month=month,
                total_hours=current_month_hours,
                converted_days=total_days_to_convert,
                remaining_hours=remaining_hours,
                carried_hours=carried_hours,
                processed=True,
                processing_date=datetime.now()
            )
            
            db.session.add(monthly_balance)
            
            # إذا كان هناك أيام للتحويل، أنشئ إجازة سنوية
            if total_days_to_convert > 0:
                # تحديث رصيد الإجازات أولاً
                balance = LeaveBalance.query.filter_by(
                    employee_id=employee_id,
                    year=year
                ).first()
                
                if not balance:
                    balance = LeaveBalance(
                        employee_id=employee_id,
                        year=year,
                        current_year_balance=30,
                        previous_year_balance=0,
                        sick_leave_balance=7
                    )
                    db.session.add(balance)
                
                # التحقق من كفاية الرصيد قبل الترحيل
                remaining_annual = balance.get_remaining_annual_balance()
                if total_days_to_convert > remaining_annual:
                    # يمكن إما تسجيل تحذير أو ترحيل الحد الأقصى المتاح فقط
                    flash(f'تحذير: الموظف {employee_id} لا يملك رصيد كافي لترحيل {total_days_to_convert} أيام. المتبقي: {remaining_annual}', 'warning')
                    total_days_to_convert = remaining_annual
                
                if total_days_to_convert > 0:  # التأكد من وجود أيام للترحيل
                    notes_parts = []
                    if days_to_convert > 0:
                        notes_parts.append(f'تحويل {total_hours:.2f} ساعة إلى {days_to_convert} يوم (متبقي: {remaining_hours:.2f} ساعة)')
                    if long_departure_days > 0:
                        notes_parts.append(f'ترحيل {long_departure_days} مغادرة طويلة (فوق 4 ساعات)')
                    
                    leave_deduction = Leave(
                        employee_id=employee_id,
                        leave_type='إجازة سنوية',
                        start_date=end_date.date(),
                        end_date=end_date.date(),
                        days_count=total_days_to_convert,
                        reason=f'ترحيل مغادرات شهر {month}/{year}',
                        notes=' | '.join(notes_parts)
                    )
                    
                    db.session.add(leave_deduction)
                    db.session.flush()  # للحصول على ID الإجازة
                    
                    # إنشاء سجلات ConvertedDeparture للمغادرات القصيرة
                    if days_to_convert > 0:
                        for dep in short_deps:
                            converted_departure = ConvertedDeparture(
                                employee_id=employee_id,
                                original_departure_date=dep.start_date,
                                original_start_time=dep.start_time or datetime.strptime('08:00', '%H:%M').time(),
                                original_end_time=dep.end_time or datetime.strptime('12:00', '%H:%M').time(),
                                original_hours_count=dep.hours_count or 0,
                                converted_to_leave_type='إجازة سنوية',
                                converted_days_count=int(dep.hours_count // 7) if dep.hours_count else 0,
                                original_reason=dep.reason,
                                original_notes=dep.notes,
                                conversion_date=datetime.now(),
                                leave_id=leave_deduction.id
                            )
                            db.session.add(converted_departure)
                    
                    # إنشاء سجلات ConvertedDeparture للمغادرات الطويلة
                    if long_departure_days > 0:
                        for dep in long_deps:
                            converted_departure = ConvertedDeparture(
                                employee_id=employee_id,
                                original_departure_date=dep.start_date,
                                original_start_time=dep.start_time or datetime.strptime('08:00', '%H:%M').time(),
                                original_end_time=dep.end_time or datetime.strptime('16:00', '%H:%M').time(),
                                original_hours_count=dep.hours_count or 8,
                                converted_to_leave_type='إجازة سنوية',
                                converted_days_count=1,  # كل مغادرة طويلة = يوم واحد
                                original_reason=dep.reason,
                                original_notes=dep.notes,
                                conversion_date=datetime.now(),
                                leave_id=leave_deduction.id
                            )
                            db.session.add(converted_departure)
                    
                    # خصم الأيام من الرصيد
                    balance.used_annual_leave += total_days_to_convert
            
            processed_employees += 1
        
        db.session.commit()
        flash(f'تم ترحيل مغادرات شهر {month}/{year} بنجاح. تم معالجة {processed_employees} موظف', 'success')
        return redirect(url_for('leave.process_monthly_departures'))
    
    # عرض الشهور المعالجة
    processed_months = db.session.query(
        MonthlyDepartureBalance.year,
        MonthlyDepartureBalance.month,
        func.count(MonthlyDepartureBalance.id).label('employee_count'),
        func.sum(MonthlyDepartureBalance.converted_days).label('total_converted_days')
    ).filter(
        MonthlyDepartureBalance.processed == True
    ).group_by(
        MonthlyDepartureBalance.year,
        MonthlyDepartureBalance.month
    ).order_by(
        MonthlyDepartureBalance.year.desc(),
        MonthlyDepartureBalance.month.desc()
    ).all()
    
    return render_template('process_monthly_departures.html', processed_months=processed_months)

# عرض تفاصيل الترحيل الشهري
@leave.route('/monthly_departure_details/<int:year>/<int:month>')
def monthly_departure_details(year, month):
    # الحصول على تفاصيل الترحيل للشهر المحدد
    monthly_balances = MonthlyDepartureBalance.query.filter_by(
        year=year,
        month=month,
        processed=True
    ).join(Employee).order_by(Employee.name).all()
    
    return render_template('monthly_departure_details.html', 
                         monthly_balances=monthly_balances,
                         year=year,
                         month=month)

# تعديل رصيد الإجازات
# احذف الأسطر من 399-416 بالكامل (دالة edit_leave_balance المعلقة)
# @leave.route('/edit_leave_balance/<int:employee_id>', methods=['GET', 'POST'])
# def edit_leave_balance(employee_id):
#     employee = Employee.query.get_or_404(employee_id)
#     
#     if request.method == 'POST':
#         employee.current_year_leave_balance = int(request.form.get('current_year_leave_balance', 30))
#         employee.previous_year_leave_balance = int(request.form.get('previous_year_leave_balance', 0))
#         employee.sick_leave_balance = int(request.form.get('sick_leave_balance', 7))
#         
#         try:
#             db.session.commit()
#             flash('تم تحديث رصيد الإجازات بنجاح', 'success')
#             return redirect(url_for('main.leave_balances'))
#         except Exception as e:
#             db.session.rollback()
#             flash('حدث خطأ أثناء تحديث رصيد الإجازات', 'error')
#     
#     return render_template('edit_leave_balance.html', employee=employee)

# إضافة إجازة جديدة
# في بداية الملف، أضف import
from constants import LEAVE_TYPES

@leave.route('/leaves/add', methods=['GET', 'POST'])
@permission_required('can_manage_leaves')
def add_leave():
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        
        # التحقق من أن الموظف من موظفي المديرية
        employee = Employee.query.get_or_404(employee_id)
        if not employee.is_directorate_employee:
            flash('الإجازات متاحة لموظفي المديرية فقط', 'danger')
            return redirect(url_for('leave.leaves'))
        
        leave_type = request.form.get('leave_type')
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
        end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d')
        
        # حساب عدد الأيام تلقائياً
        days_count_form = request.form.get('days_count')
        if days_count_form:
            days_count = int(days_count_form)
        else:
            # حساب عدد الأيام من التواريخ
            days_count = (end_date - start_date).days + 1
        
        reason = request.form.get('reason')
        notes = request.form.get('notes')
        
        # التحقق من الرصيد للإجازات السنوية والمرضية
        if leave_type in ['إجازة سنوية', 'إجازة اعتيادية', 'إجازة مرضية']:
            current_year = start_date.year
            balance = LeaveBalance.query.filter_by(
                employee_id=employee_id, 
                year=current_year
            ).first()
            
            if not balance:
                # إنشاء رصيد جديد
                balance = LeaveBalance(
                    employee_id=employee_id,
                    year=current_year,
                    current_year_balance=30,
                    previous_year_balance=0,
                    sick_leave_balance=7
                )
                db.session.add(balance)
                db.session.commit()
            
            # التحقق من الرصيد
            if leave_type in ['إجازة سنوية', 'إجازة اعتيادية']:
                remaining_annual = balance.get_remaining_annual_balance()
                if days_count > remaining_annual:
                    flash(f'الرصيد المتبقي من الإجازات السنوية غير كافي. المتبقي: {remaining_annual} يوم', 'danger')
                    return redirect(url_for('leave.add_leave'))
            
            elif leave_type == 'إجازة مرضية':
                remaining_sick = balance.get_remaining_sick_balance()
                if days_count > remaining_sick:
                    flash(f'الرصيد المتبقي من الإجازات المرضية غير كافي. المتبقي: {remaining_sick} يوم', 'danger')
                    return redirect(url_for('leave.add_leave'))
        
        # إنشاء سجل الإجازة
        new_leave = Leave(
            employee_id=employee_id,
            leave_type=leave_type,
            start_date=start_date.date(),
            end_date=end_date.date(),
            days_count=days_count,
            reason=reason,
            notes=notes
        )
        
        db.session.add(new_leave)
        
        # تحديث الرصيد المستخدم
        if leave_type in ['إجازة سنوية', 'إجازة اعتيادية']:
            balance.used_annual_leave += days_count
        elif leave_type == 'إجازة مرضية':
            balance.used_sick_leave += days_count
        
        db.session.commit()
        
        # تسجيل العملية في سجلات المستخدمين
        log_user_activity(
            user_id=session.get('user_id'),
            action='إضافة',
            module='الإجازات',
            description=f'تم إضافة إجازة {leave_type} للموظف: {employee.name}',
            target_id=new_leave.id,
            target_type='إجازة'
        )
        
        flash('تم إضافة الإجازة بنجاح', 'success')
        return redirect(url_for('leave.leaves'))
    
    # الحصول على قائمة موظفي المديرية فقط للاختيار
    employees = Employee.query.filter_by(is_directorate_employee=True).order_by(Employee.name).all()
    
    return render_template('leave_form.html', employees=employees, leave=None, leave_types=LEAVE_TYPES)

# تعديل إجازة
@leave.route('/leaves/edit/<int:id>', methods=['GET', 'POST'])
def edit_leave(id):
    leave = Leave.query.get_or_404(id)
    
    # التأكد من أن السجل ليس مغادرة
    if leave.leave_type == 'مغادرة':
        flash('لا يمكن تعديل المغادرات من هنا', 'danger')
        return redirect(url_for('leave.leaves'))

    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        
        # التحقق من أن الموظف من موظفي المديرية
        employee = Employee.query.get_or_404(employee_id)
        if not employee.is_directorate_employee:
            flash('الإجازات متاحة لموظفي المديرية فقط', 'danger')
            return redirect(url_for('leave.leaves'))

        leave_type = request.form.get('leave_type')
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
        end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d')
        
        # حساب عدد الأيام تلقائياً
        days_count_form = request.form.get('days_count')
        if days_count_form:
            days_count = int(days_count_form)
        else:
            # حساب عدد الأيام من التواريخ
            days_count = (end_date - start_date).days + 1

        reason = request.form.get('reason')
        notes = request.form.get('notes')
        
        # الحصول على الرصيد للموظف الجديد (في حالة تغيير الموظف)
        current_year = start_date.year
        balance = LeaveBalance.query.filter_by(
            employee_id=employee_id,
            year=current_year
        ).first()
        
        if not balance:
            balance = LeaveBalance(
                employee_id=employee_id,
                year=current_year,
                current_year_balance=30,
                previous_year_balance=0,
                sick_leave_balance=7
            )
            db.session.add(balance)
        
        # إرجاع الرصيد القديم للموظف القديم
        old_balance = LeaveBalance.query.filter_by(
            employee_id=leave.employee_id,
            year=current_year
        ).first()
        
        if old_balance:
            if leave.leave_type in ['إجازة سنوية', 'إجازة اعتيادية', 'سنوية']:
                old_balance.used_annual_leave -= leave.days_count
                if old_balance.used_annual_leave < 0:
                    old_balance.used_annual_leave = 0
            elif leave.leave_type == 'إجازة مرضية':
                old_balance.used_sick_leave -= leave.days_count
                if old_balance.used_sick_leave < 0:
                    old_balance.used_sick_leave = 0
        
        # التحقق من الرصيد المتاح للإجازة الجديدة
        if leave_type in ['إجازة سنوية', 'إجازة اعتيادية', 'سنوية']:
            remaining_annual = balance.get_remaining_annual_balance()
            if days_count > remaining_annual:
                flash(f'الرصيد المتبقي من الإجازات السنوية غير كافي. المتبقي: {remaining_annual} يوم', 'danger')
                return redirect(url_for('leave.edit_leave', id=id))
        
        elif leave_type == 'إجازة مرضية':
            remaining_sick = balance.get_remaining_sick_balance()
            if days_count > remaining_sick:
                flash(f'الرصيد المتبقي من الإجازات المرضية غير كافي. المتبقي: {remaining_sick} يوم', 'danger')
                return redirect(url_for('leave.edit_leave', id=id))
        
        # تحديث سجل الإجازة
        leave.employee_id = employee_id
        leave.leave_type = leave_type
        leave.start_date = start_date.date()
        leave.end_date = end_date.date()
        leave.days_count = days_count
        leave.reason = reason
        leave.notes = notes
        
        # خصم الرصيد الجديد
        if leave_type in ['إجازة سنوية', 'إجازة اعتيادية', 'سنوية']:
            balance.used_annual_leave += days_count
        elif leave_type == 'إجازة مرضية':
            balance.used_sick_leave += days_count
        
        db.session.commit()
        
        flash('تم تحديث الإجازة بنجاح', 'success')
        return redirect(url_for('leave.leaves'))

    # الحصول على قائمة موظفي المديرية فقط للاختيار
    employees = Employee.query.filter_by(is_directorate_employee=True).order_by(Employee.name).all()
    
    return render_template('leave_form.html', employees=employees, leave=leave, leave_types=LEAVE_TYPES)

# حذف إجازة
@leave.route('/leaves/delete/<int:id>', methods=['POST'])
@permission_required('can_manage_leaves')
def delete_leave(id):
    leave = Leave.query.get_or_404(id)
    employee_name = leave.employee.name  # حفظ اسم الموظف قبل الحذف
    leave_type = leave.leave_type  # حفظ نوع الإجازة قبل الحذف
    
    # إرجاع الرصيد عند حذف الإجازة
    current_year = datetime.now().year
    balance = LeaveBalance.query.filter_by(
        employee_id=leave.employee_id,
        year=current_year
    ).first()
    
    if balance:
        if leave.leave_type in ['إجازة سنوية', 'إجازة اعتيادية', 'سنوية']:
            balance.used_annual_leave -= leave.days_count
            if balance.used_annual_leave < 0:
                balance.used_annual_leave = 0
        elif leave.leave_type == 'إجازة مرضية':
            balance.used_sick_leave -= leave.days_count
            if balance.used_sick_leave < 0:
                balance.used_sick_leave = 0
    
    db.session.delete(leave)
    db.session.commit()
    
    # تسجيل العملية في سجلات المستخدمين
    log_user_activity(
        user_id=session.get('user_id'),
        action='حذف',
        module='الإجازات',
        description=f'تم حذف إجازة {leave_type} للموظف: {employee_name}',
        target_id=id,
        target_type='إجازة'
    )
    
    flash('تم حذف الإجازة بنجاح وإرجاع الرصيد', 'success')
    return redirect(url_for('leave.leaves'))

# صفحة رصيد الإجازات
@leave.route('/leave_balances')
def leave_balances():
    search_term = request.args.get('search', '')
    current_year = datetime.now().year
    
    # بناء استعلام موظفي المديرية فقط
    query = Employee.query.filter(Employee.is_directorate_employee == True)
    
    if search_term:
        query = query.filter(
            db.or_(
                Employee.name.contains(search_term),
                Employee.civil_id.contains(search_term),
                Employee.ministry_number.contains(search_term)
            )
        )
    
    employees = query.order_by(Employee.name).all()
    
    # إنشاء قاموس لأرصدة الموظفين
    balances_dict = {}
    for employee in employees:
        # البحث عن رصيد السنة الحالية
        balance = LeaveBalance.query.filter_by(
            employee_id=employee.id, 
            year=current_year
        ).first()
        
        if not balance:
            # إنشاء رصيد جديد إذا لم يكن موجوداً
            balance = LeaveBalance(
                employee_id=employee.id,
                year=current_year,
                current_year_balance=30,
                previous_year_balance=0,
                sick_leave_balance=7
            )
            db.session.add(balance)
        
        # حساب الإجازات المستخدمة
        used_annual = db.session.query(func.sum(Leave.days_count)).filter(
            Leave.employee_id == employee.id,
            Leave.leave_type.in_(['إجازة سنوية', 'إجازة اعتيادية']),
            func.extract('year', Leave.start_date) == current_year
        ).scalar() or 0
        
        used_sick = db.session.query(func.sum(Leave.days_count)).filter(
            Leave.employee_id == employee.id,
            Leave.leave_type == 'إجازة مرضية',
            func.extract('year', Leave.start_date) == current_year
        ).scalar() or 0
        
        # تحديث الإجازات المستخدمة
        balance.used_annual_leave = used_annual
        balance.used_sick_leave = used_sick
        
        balances_dict[employee.id] = balance
    
    db.session.commit()
    
    return render_template('leave_balances.html',
                         employees=employees,
                         balances_dict=balances_dict,
                         search_term=search_term,
                         current_year=current_year)

# تعديل رصيد الإجازات
@leave.route('/leave_balances/edit/<int:employee_id>', methods=['GET', 'POST'])
@permission_required('can_manage_leaves')
def edit_leave_balance(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    
    # التأكد من أن الموظف من موظفي المديرية
    if not employee.is_directorate_employee:
        flash('رصيد الإجازات متاح لموظفي المديرية فقط', 'danger')
        return redirect(url_for('leave.leave_balances'))
    
    current_year = datetime.now().year
    balance = LeaveBalance.query.filter_by(
        employee_id=employee.id, 
        year=current_year
    ).first()
    
    if not balance:
        balance = LeaveBalance(
        employee_id=employee.id,
        year=current_year,
        current_year_balance=30,
        previous_year_balance=0,
        sick_leave_balance=7
    )
    db.session.add(balance)
    db.session.commit()
    
    if request.method == 'POST':
        balance.current_year_balance = int(request.form.get('current_year_balance'))
        balance.previous_year_balance = int(request.form.get('previous_year_balance'))
        balance.sick_leave_balance = int(request.form.get('sick_leave_balance'))
        
        db.session.commit()
        flash('تم تحديث رصيد الإجازات بنجاح', 'success')
        return redirect(url_for('leave.leave_balances'))
    
    return render_template('leave_balance_form.html',
                         employee=employee,
                         balance=balance)

@leave.route('/print_leave_balances')
@login_required
def print_leave_balances():
    search_term = request.args.get('search', '')
    current_year = datetime.now().year
    
    query = LeaveBalance.query.join(Employee).filter(LeaveBalance.year == current_year)
    
    if search_term:
        query = query.filter(
            or_(
                Employee.name.contains(search_term),
                Employee.employee_id.contains(search_term)
            )
        )
    
    leave_balances = query.all()
    
    # تحضير بيانات الموظفين مع الإجازات المستخدمة
    employees_data = []
    
    for balance in leave_balances:
        employee = balance.employee
        
        # جلب جميع الإجازات للسنة الحالية
        all_leaves = Leave.query.filter(
            Leave.employee_id == employee.id,
            db.extract('year', Leave.start_date) == current_year
        ).all()
        
        # تصنيف الإجازات حسب النوع
        annual_leaves = []
        sick_leaves = []
        
        for leave in all_leaves:
            if leave.leave_type:
                leave_type = leave.leave_type.strip().lower()
                
                # تصنيف شامل للإجازات السنوية - تحسين المنطق
                if (any(keyword in leave_type for keyword in ['سنوية', 'اعتيادية', 'عادية', 'annual']) or
                    leave_type in ['إجازة سنوية', 'إجازة اعتيادية', 'سنوية', 'اعتيادية', 'عادية']):
                    annual_leaves.append(leave)
                    
                # تصنيف شامل للإجازات المرضية
                elif (any(keyword in leave_type for keyword in ['مرضية', 'مرض', 'sick']) or
                      leave_type in ['إجازة مرضية', 'مرضية', 'مرض']):
                    sick_leaves.append(leave)
                    
                # تصنيف الإجازات الأخرى حسب السياق
                elif any(keyword in leave_type for keyword in ['طارئة', 'عاجلة', 'ضرورية']):
                    annual_leaves.append(leave)  # تصنف كإجازة سنوية
                    
                # إذا لم يتم التعرف على النوع، تصنف كإجازة سنوية (افتراضي)
                else:
                    annual_leaves.append(leave)
                    print(f"تم تصنيف '{leave_type}' كإجازة سنوية")
        
        employees_data.append({
            'employee': employee,
            'balance': balance,
            'annual_leaves': annual_leaves,
            'sick_leaves': sick_leaves
        })
    
    return render_template('print_leave_balances.html', 
                         employees_data=employees_data,
                         current_year=current_year,
                         search_term=search_term,
                         print_date=datetime.now())


@leave.route('/print_employee_balance/<int:employee_id>')
@login_required
def print_employee_balance(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    balance = LeaveBalance.query.filter_by(employee_id=employee_id).first()
    
    if not balance:
        flash('لا يوجد رصيد إجازات لهذا الموظف', 'warning')
        return redirect(url_for('leave.leave_balances'))
    
    # جلب إجازات السنة الحالية (استبعاد المغادرات العادية)
    current_year = datetime.now().year
    all_leaves = Leave.query.filter(
        Leave.employee_id == employee_id,
        db.extract('year', Leave.start_date) == current_year,
        Leave.leave_type != 'مغادرة'  # استبعاد المغادرات العادية
    ).all()
    
    # تصنيف الإجازات مع معلومات إضافية
    annual_leaves = []
    sick_leaves = []
    converted_departures = []
    
    for leave in all_leaves:
        # إضافة معلومات إضافية لكل إجازة
        leave_info = {
            'leave': leave,
            'category': '',
            'converted_month': None
        }
        
        if leave.leave_type:
            leave_type = leave.leave_type.strip().lower()
            
            # فحص إذا كانت مغادرة محولة
            if 'ترحيل مغادرات' in (leave.reason or ''):
                # استخراج الشهر من السبب
                import re
                month_match = re.search(r'ترحيل مغادرات شهر (\d+)/(\d+)', leave.reason or '')
                if month_match:
                    month = month_match.group(1)
                    year = month_match.group(2)
                    leave_info['converted_month'] = f"{month}/{year}"
                
                leave_info['category'] = 'ترحيل مغادرات'
                converted_departures.append(leave_info)
                
            # تصنيف الإجازات السنوية
            elif (any(keyword in leave_type for keyword in ['سنوية', 'اعتيادية', 'عادية', 'annual']) or
                  leave_type in ['إجازة سنوية', 'إجازة اعتيادية', 'سنوية', 'اعتيادية', 'عادية']):
                leave_info['category'] = 'سنوية'
                annual_leaves.append(leave_info)
                
            # تصنيف الإجازات المرضية
            elif (any(keyword in leave_type for keyword in ['مرضية', 'مرض', 'sick']) or
                  leave_type in ['إجازة مرضية', 'مرضية', 'مرض']):
                leave_info['category'] = 'مرضية'
                sick_leaves.append(leave_info)
                
            # الإجازات الأخرى تصنف كسنوية
            else:
                leave_info['category'] = 'سنوية'
                annual_leaves.append(leave_info)
    
    return render_template('print_employee_balance.html',
                         employee=employee,
                         balance=balance,
                         annual_leaves=annual_leaves,
                         sick_leaves=sick_leaves,
                         converted_departures=converted_departures,
                         current_year=current_year,
                         print_date=datetime.now())


@leave.route('/converted_departures')
def converted_departures():
    # الحصول على معاملات الفلترة
    employee_id = request.args.get('employee_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    leave_type = request.args.get('leave_type')
    
    # بناء الاستعلام للحصول على البيانات المجمعة
    query = db.session.query(
        Leave.id.label('leave_id'),
        Leave.employee_id,
        Employee.name.label('employee_name'),
        Leave.reason,
        Leave.start_date,
        Leave.days_count,
        Leave.notes,
        func.count(ConvertedDeparture.id).label('total_departures'),
        func.sum(ConvertedDeparture.original_hours_count).label('total_hours')
    ).select_from(Leave).join(
        ConvertedDeparture, Leave.id == ConvertedDeparture.leave_id
    ).join(
        Employee, Leave.employee_id == Employee.id
    ).filter(
        Leave.reason.like('%ترحيل مغادرات شهر%')
    )
    
    # تطبيق الفلاترة
    if employee_id:
        query = query.filter(Leave.employee_id == employee_id)
    
    if start_date:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        query = query.filter(Leave.start_date >= start_date_obj)
    
    if end_date:
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        query = query.filter(Leave.start_date <= end_date_obj)
    
    # تجميع النتائج
    converted_departures = query.group_by(
        Leave.id, Leave.employee_id, Employee.name, Leave.reason, 
        Leave.start_date, Leave.days_count, Leave.notes
    ).order_by(Leave.start_date.desc()).all()
    
    # الحصول على قائمة الموظفين للفلترة
    employees = Employee.query.order_by(Employee.name).all()
    
    # أنواع الإجازات المتاحة
    leave_types = ['سنوية', 'مرضية', 'طارئة', 'بدون راتب']
    
    return render_template('converted_departures.html', 
                         converted_departures=converted_departures,
                         employees=employees,
                         leave_types=leave_types,
                         filters={
                             'employee_id': employee_id,
                             'start_date': start_date,
                             'end_date': end_date,
                             'leave_type': leave_type
                         })

# تعديل مغادرة
@leave.route('/departures/edit/<int:id>', methods=['GET', 'POST'])
@permission_required('can_manage_leaves')
def edit_departure(id):
    departure = Leave.query.get_or_404(id)
    
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        
        # التحقق من أن الموظف من موظفي المديرية
        employee = Employee.query.get_or_404(employee_id)
        if not employee.is_directorate_employee:
            flash('المغادرات متاحة لموظفي المديرية فقط', 'danger')
            return redirect(url_for('leave.departures'))
        
        departure_date = datetime.strptime(request.form.get('departure_date'), '%Y-%m-%d')
        start_time = datetime.strptime(request.form.get('start_time'), '%H:%M').time()
        end_time = datetime.strptime(request.form.get('end_time'), '%H:%M').time()
        reason = request.form.get('reason')
        notes = request.form.get('notes')
        
        # حساب عدد الساعات
        start_datetime = datetime.combine(departure_date, start_time)
        end_datetime = datetime.combine(departure_date, end_time)
        
        # إذا كان وقت الانتهاء أقل من وقت البداية، فهذا يعني أن الانتهاء في اليوم التالي
        if end_time < start_time:
            end_datetime = end_datetime.replace(day=end_datetime.day + 1)
        
        hours_count = (end_datetime - start_datetime).total_seconds() / 3600
        
        # تحديث بيانات المغادرة فقط (بدون تحويل مباشر)
        departure.employee_id = employee_id
        departure.leave_type = 'مغادرة'  # دائماً مغادرة
        departure.start_date = departure_date.date()
        departure.end_date = departure_date.date()
        departure.days_count = 0  # المغادرات لا تحسب كأيام إجازة مباشرة
        departure.start_time = start_time
        departure.end_time = end_time
        departure.hours_count = hours_count
        departure.reason = reason
        departure.notes = notes
        
        db.session.commit()
        
        # تسجيل العملية في سجلات المستخدمين
        log_user_activity(
            user_id=session.get('user_id'),
            action='تعديل',
            module='المغادرات',
            description=f'تم تعديل مغادرة الموظف: {employee.name} في تاريخ {departure_date.date()}',
            target_id=departure.id,
            target_type='مغادرة'
        )
        
        flash('تم تحديث المغادرة بنجاح', 'success')
        return redirect(url_for('leave.departures'))
    
    # الحصول على قائمة الموظفين للاختيار
    employees = Employee.query.filter_by(is_directorate_employee=True).order_by(Employee.name).all()
    
    return render_template('departure_form.html', employees=employees, departure=departure)

# صفحة تفريغ سجل المغادرات المحولة
@leave.route('/converted_departures/clear_all', methods=['POST'])
@permission_required('can_manage_leaves')
def clear_converted_departures():
    try:
        # الحصول على جميع سجلات المغادرات المحولة قبل حذفها
        converted_departures = ConvertedDeparture.query.all()
        
        # حذف الإجازات المرحلة المرتبطة
        deleted_leaves_count = 0
        for converted_departure in converted_departures:
            # البحث عن الإجازة المرحلة المرتبطة
            if converted_departure.leave_id:
                leave_to_delete = Leave.query.get(converted_departure.leave_id)
                if leave_to_delete:
                    # استرداد الأيام من رصيد الإجازات
                    leave_balance = LeaveBalance.query.filter_by(
                        employee_id=converted_departure.employee_id,
                        year=leave_to_delete.start_date.year
                    ).first()
                    
                    if leave_balance:
                        leave_balance.used_annual_leave -= leave_to_delete.days_count
                        if leave_balance.used_annual_leave < 0:
                            leave_balance.used_annual_leave = 0
                    
                    # حذف سجل الإجازة
                    db.session.delete(leave_to_delete)
                    deleted_leaves_count += 1
            else:
                # البحث عن الإجازة بناءً على السبب إذا لم يكن هناك ربط مباشر
                leave_to_delete = Leave.query.filter(
                    Leave.employee_id == converted_departure.employee_id,
                    Leave.leave_type == converted_departure.converted_to_leave_type,
                    Leave.reason.like('%ترحيل مغادرات%')
                ).first()
                
                if leave_to_delete:
                    # استرداد الأيام من رصيد الإجازات
                    leave_balance = LeaveBalance.query.filter_by(
                        employee_id=converted_departure.employee_id,
                        year=leave_to_delete.start_date.year
                    ).first()
                    
                    if leave_balance:
                        leave_balance.used_annual_leave -= leave_to_delete.days_count
                        if leave_balance.used_annual_leave < 0:
                            leave_balance.used_annual_leave = 0
                    
                    # حذف سجل الإجازة
                    db.session.delete(leave_to_delete)
                    deleted_leaves_count += 1
        
        # حذف جميع سجلات المغادرات المحولة
        deleted_count = ConvertedDeparture.query.delete()
        
        # حذف جميع سجلات الترحيل الشهري
        monthly_balances_deleted = MonthlyDepartureBalance.query.delete()
        
        db.session.commit()
        
        flash(f'تم تفريغ سجل المغادرات المحولة بنجاح. تم حذف {deleted_count} سجل مغادرة محولة، {deleted_leaves_count} إجازة مرحلة، و {monthly_balances_deleted} سجل ترحيل شهري', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء تفريغ السجل: {str(e)}', 'danger')
    
    return redirect(url_for('leave.converted_departures'))

# إلغاء ترحيل شهري
@leave.route('/cancel_monthly_processing/<int:year>/<int:month>', methods=['POST'])
@permission_required('can_manage_leaves')
def cancel_monthly_processing(year, month):
    try:
        # الحصول على سجلات الترحيل للشهر المحدد
        monthly_balances = MonthlyDepartureBalance.query.filter_by(
            year=year,
            month=month,
            processed=True
        ).all()
        
        if not monthly_balances:
            flash(f'لا توجد بيانات ترحيل لشهر {month}/{year}', 'warning')
            return redirect(url_for('leave.process_monthly_departures'))
        
        # حذف الإجازات السنوية المُنشأة من الترحيل
        for balance in monthly_balances:
            # البحث عن الإجازة السنوية المُنشأة من الترحيل
            leave_to_delete = Leave.query.filter(
                Leave.employee_id == balance.employee_id,
                Leave.leave_type == 'إجازة سنوية',
                Leave.reason.like(f'%ترحيل مغادرات شهر {month}/{year}%')
            ).first()
            
            if leave_to_delete:
                # حذف سجلات ConvertedDeparture المرتبطة بهذه الإجازة
                ConvertedDeparture.query.filter_by(leave_id=leave_to_delete.id).delete()
                
                # استرداد الأيام من رصيد الإجازات
                leave_balance = LeaveBalance.query.filter_by(
                    employee_id=balance.employee_id,
                    year=year
                ).first()
                
                if leave_balance:
                    leave_balance.used_annual_leave -= leave_to_delete.days_count
                    if leave_balance.used_annual_leave < 0:
                        leave_balance.used_annual_leave = 0
                
                # حذف سجل الإجازة
                db.session.delete(leave_to_delete)
        
        # حذف سجلات الترحيل الشهري
        for balance in monthly_balances:
            db.session.delete(balance)
        
        db.session.commit()
        
        flash(f'تم إلغاء ترحيل شهر {month}/{year} بنجاح وحذف جميع البيانات المرتبطة', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء إلغاء الترحيل: {str(e)}', 'danger')
    
    return redirect(url_for('leave.process_monthly_departures'))

@leave.route('/departure_details/<int:leave_id>')
def departure_details(leave_id):
    # الحصول على تفاصيل المغادرات المرحلة
    departures = ConvertedDeparture.query.filter_by(leave_id=leave_id).all()
    
    if not departures:
        return "<p>لا توجد تفاصيل متاحة</p>"
    
    html = "<table class='table table-sm'>"
    html += "<thead><tr><th>تاريخ المغادرة</th><th>من</th><th>إلى</th><th>الساعات</th><th>السبب</th></tr></thead>"
    html += "<tbody>"
    
    for dep in departures:
        html += f"<tr>"
        html += f"<td>{dep.original_departure_date.strftime('%Y-%m-%d')}</td>"
        html += f"<td>{dep.original_start_time.strftime('%H:%M')}</td>"
        html += f"<td>{dep.original_end_time.strftime('%H:%M')}</td>"
        html += f"<td>{dep.original_hours_count:.1f}</td>"
        html += f"<td>{dep.original_reason or '-'}</td>"
        html += f"</tr>"
    
    html += "</tbody></table>"
    
    return html