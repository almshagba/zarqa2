from flask import Blueprint, request, make_response, session, redirect, url_for
from database import db
from models import Employee, Leave, LeaveBalance, ConvertedDeparture, MonthlyDepartureBalance, School
from datetime import datetime
import pandas as pd
from io import BytesIO
from urllib.parse import quote
from routes.auth_routes import admin_required, login_required, permission_required
from sqlalchemy import func  # إضافة هذا السطر

export = Blueprint('export', __name__, url_prefix='/export')

@export.route('/employee_balances')
# استبدال @admin_required بـ:
@permission_required('can_export_data')
def export_employee_balances():
    """تصدير أرصدة جميع الموظفين إلى Excel"""
    current_year = datetime.now().year
    
    # الحصول على جميع أرصدة الموظفين للسنة الحالية
    balances = db.session.query(
        Employee.ministry_number,
        Employee.name,
        Employee.civil_id,
        Employee.job_title,
        School.name.label('school_name'),
        LeaveBalance.current_year_balance,
        LeaveBalance.previous_year_balance,
        LeaveBalance.sick_leave_balance,
        LeaveBalance.used_annual_leave,
        LeaveBalance.used_sick_leave
    ).join(LeaveBalance).join(School, Employee.school_id == School.id).filter(
        LeaveBalance.year == current_year
        # إزالة فلتر موظفي المديرية لإظهار جميع الموظفين
    ).order_by(Employee.name).all()
    
    # إنشاء البيانات للتصدير
    data = []
    for balance in balances:
        remaining_annual = (balance.current_year_balance + balance.previous_year_balance) - balance.used_annual_leave
        remaining_sick = balance.sick_leave_balance - balance.used_sick_leave
        
        data.append({
            'الرقم الوزاري': balance.ministry_number,
            'اسم الموظف': balance.name,
            'الرقم المدني': balance.civil_id,
            'الوظيفة': balance.job_title,
            'المدرسة': balance.school_name,
            'رصيد السنة الحالية': balance.current_year_balance,
            'رصيد السنة السابقة': balance.previous_year_balance,
            'إجمالي الرصيد السنوي': balance.current_year_balance + balance.previous_year_balance,
            'الإجازات السنوية المستخدمة': balance.used_annual_leave,
            'الرصيد السنوي المتبقي': remaining_annual,
            'رصيد الإجازات المرضية': balance.sick_leave_balance,
            'الإجازات المرضية المستخدمة': balance.used_sick_leave,
            'الرصيد المرضي المتبقي': remaining_sick
        })
    
    return create_excel_response(data, f'أرصدة الموظفين {current_year}')

@export.route('/leaves_log')
@permission_required('can_export_data')
def export_leaves_log():
    """تصدير سجل الإجازات إلى Excel"""
    year = request.args.get('year', datetime.now().year, type=int)
    
    # الحصول على جميع الإجازات للسنة المحددة
    leaves = db.session.query(
        Employee.ministry_number,
        Employee.name,
        Employee.civil_id,
        Employee.job_title,
        School.name.label('school_name'),
        Leave.leave_type,
        Leave.start_date,
        Leave.end_date,
        Leave.days_count,
        Leave.reason,
        Leave.notes,
        Leave.created_at
    ).join(Employee, Leave.employee_id == Employee.id).join(School, Employee.school_id == School.id).filter(
        db.extract('year', Leave.start_date) == year,
        # تم إزالة فلتر استبعاد موظفي المديرية
        Leave.leave_type != 'مغادرة'  # استبعاد المغادرات
    ).order_by(Leave.start_date.desc()).all()
    
    # إنشاء البيانات للتصدير
    data = []
    for leave in leaves:
        data.append({
            'الرقم الوزاري': leave.ministry_number,
            'اسم الموظف': leave.name,
            'الرقم المدني': leave.civil_id,
            'الوظيفة': leave.job_title,
            'المدرسة': leave.school_name,
            'نوع الإجازة': leave.leave_type,
            'تاريخ البداية': leave.start_date.strftime('%Y-%m-%d'),
            'تاريخ النهاية': leave.end_date.strftime('%Y-%m-%d'),
            'عدد الأيام': leave.days_count,
            'السبب': leave.reason or '',
            'ملاحظات': leave.notes or '',
            'تاريخ التسجيل': leave.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    return create_excel_response(data, f'سجل الإجازات {year}')

@export.route('/departures_log')
@permission_required('can_export_data')
def export_departures_log():
    """تصدير سجل المغادرات إلى Excel"""
    year = request.args.get('year', datetime.now().year, type=int)
    
    # الحصول على جميع المغادرات للسنة المحددة
    departures = db.session.query(
        Employee.ministry_number,
        Employee.name,
        Employee.civil_id,
        Employee.job_title,
        School.name.label('school_name'),
        Leave.start_date,
        Leave.start_time,
        Leave.end_time,
        Leave.hours_count,
        Leave.reason,
        Leave.notes,
        Leave.created_at
    ).join(Employee, Leave.employee_id == Employee.id).join(School, Employee.school_id == School.id).filter(
        db.extract('year', Leave.start_date) == year,
        Employee.is_directorate_employee == True,  # موظفي المديرية فقط
        Leave.leave_type == 'مغادرة'  # المغادرات فقط
    ).order_by(Leave.start_date.desc()).all()
    
    # إنشاء البيانات للتصدير
    data = []
    for departure in departures:
        data.append({
            'الرقم الوزاري': departure.ministry_number,
            'اسم الموظف': departure.name,
            'الرقم المدني': departure.civil_id,
            'الوظيفة': departure.job_title,
            'المدرسة': departure.school_name,
            'تاريخ المغادرة': departure.start_date.strftime('%Y-%m-%d'),
            'وقت البداية': departure.start_time.strftime('%H:%M') if departure.start_time else '',
            'وقت النهاية': departure.end_time.strftime('%H:%M') if departure.end_time else '',
            'عدد الساعات': departure.hours_count or 0,
            'السبب': departure.reason or '',
            'ملاحظات': departure.notes or '',
            'تاريخ التسجيل': departure.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    return create_excel_response(data, f'سجل المغادرات {year}')

@export.route('/converted_departures')
@permission_required('can_export_data')
def export_converted_departures():
    """تصدير سجل المغادرات المحولة إلى Excel"""
    year = request.args.get('year', datetime.now().year, type=int)
    
    # الحصول علكى جميع المغادرات المحولة للسنة المحددة
    converted = db.session.query(
        Employee.ministry_number,
        Employee.name,
        Employee.civil_id,
        Employee.job_title,
        School.name.label('school_name'),
        ConvertedDeparture.original_departure_date,
        ConvertedDeparture.original_start_time,
        ConvertedDeparture.original_end_time,
        ConvertedDeparture.original_hours_count,
        ConvertedDeparture.converted_to_leave_type,
        ConvertedDeparture.converted_days_count,
        ConvertedDeparture.original_reason,
        ConvertedDeparture.conversion_date
    ).join(Employee, ConvertedDeparture.employee_id == Employee.id).join(School, Employee.school_id == School.id).filter(
        db.extract('year', ConvertedDeparture.original_departure_date) == year,
        Employee.is_directorate_employee == True  # موظفي المديرية فقط
    ).order_by(ConvertedDeparture.conversion_date.desc()).all()
    
    # إنشاء البيانات للتصدير
    data = []
    for conv in converted:
        data.append({
            'الرقم الوزاري': conv.ministry_number,
            'اسم الموظف': conv.name,
            'الرقم المدني': conv.civil_id,
            'الوظيفة': conv.job_title,
            'المدرسة': conv.school_name,
            'تاريخ المغادرة الأصلي': conv.original_departure_date.strftime('%Y-%m-%d'),
            'وقت البداية': conv.original_start_time.strftime('%H:%M'),
            'وقت النهاية': conv.original_end_time.strftime('%H:%M'),
            'عدد الساعات الأصلي': conv.original_hours_count,
            'نوع الإجازة المحولة': conv.converted_to_leave_type,
            'عدد الأيام المحولة': conv.converted_days_count,
            'السبب الأصلي': conv.original_reason or '',
            'تاريخ التحويل': conv.conversion_date.strftime('%Y-%m-%d %H:%M')
        })
    
    return create_excel_response(data, f'المغادرات المحولة {year}')

@export.route('/monthly_departure_balances')
@permission_required('can_export_data')
def export_monthly_departure_balances():
    """تصدير أرصدة المغادرات الشهرية إلى Excel"""
    year = request.args.get('year', datetime.now().year, type=int)
    
    # الحصول على جميع أرصدة المغادرات الشهرية للسنة المحددة
    monthly_balances = db.session.query(
        Employee.ministry_number,
        Employee.name,
        Employee.civil_id,
        Employee.job_title,
        School.name.label('school_name'),
        MonthlyDepartureBalance.year,
        MonthlyDepartureBalance.month,
        MonthlyDepartureBalance.total_hours,
        MonthlyDepartureBalance.converted_days,
        MonthlyDepartureBalance.remaining_hours,
        MonthlyDepartureBalance.carried_hours,
        MonthlyDepartureBalance.processed,
        MonthlyDepartureBalance.processing_date
    ).join(Employee).join(School, Employee.school_id == School.id).filter(
        MonthlyDepartureBalance.year == year,
        Employee.is_directorate_employee == False
    ).order_by(Employee.name, MonthlyDepartureBalance.month).all()
    
    # إنشاء البيانات للتصدير
    data = []
    for balance in monthly_balances:
        month_names = {
            1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل',
            5: 'مايو', 6: 'يونيو', 7: 'يوليو', 8: 'أغسطس',
            9: 'سبتمبر', 10: 'أكتوبر', 11: 'نوفمبر', 12: 'ديسمبر'
        }
        
        data.append({
            'الرقم الوزاري': balance.ministry_number,
            'اسم الموظف': balance.name,
            'الرقم المدني': balance.civil_id,
            'الوظيفة': balance.job_title,
            'المدرسة': balance.school_name,
            'السنة': balance.year,
            'الشهر': month_names.get(balance.month, str(balance.month)),
            'إجمالي الساعات': balance.total_hours,
            'الأيام المحولة': balance.converted_days,
            'الساعات المتبقية': balance.remaining_hours,
            'الساعات المنقولة': balance.carried_hours,
            'تم المعالجة': 'نعم' if balance.processed else 'لا',
            'تاريخ المعالجة': balance.processing_date.strftime('%Y-%m-%d %H:%M') if balance.processing_date else ''
        })
    
    return create_excel_response(data, f'أرصدة المغادرات الشهرية {year}')

@export.route('/converted_departures_summary')
@permission_required('can_export_data')
def export_converted_departures_summary():
    """تصدير ملخص المغادرات المحولة مع معلومات الموظف ومجموع الأيام"""
    year = request.args.get('year', type=int)
    employee_id = request.args.get('employee_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # بناء الاستعلام للحصول على البيانات المجمعة - إزالة الربط مع ConvertedDeparture
    query = db.session.query(
        Employee.ministry_number,
        Employee.name,
        School.name.label('school_name'),
        func.sum(Leave.days_count).label('total_days')
    ).select_from(Leave).join(
        Employee, Leave.employee_id == Employee.id
    ).join(
        School, Employee.school_id == School.id
    ).filter(
        Leave.reason.like('%ترحيل مغادرات شهر%')
    )
    
    # تطبيق فلاتر التاريخ فقط إذا تم تحديدها
    if start_date:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        query = query.filter(Leave.start_date >= start_date_obj)
    
    if end_date:
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        query = query.filter(Leave.start_date <= end_date_obj)
    elif year:
        query = query.filter(db.extract('year', Leave.start_date) == year)
    
    if employee_id:
        query = query.filter(Leave.employee_id == employee_id)
    
    # تجميع النتائج حسب الموظف
    results = query.group_by(
        Employee.id, Employee.ministry_number, Employee.name, School.name
    ).order_by(Employee.name).all()
    
    # إنشاء البيانات للتصدير
    data = []
    for result in results:
        # تحديد نص عدد الأيام
        days_count = result.total_days or 0
        if days_count == 1:
            days_text = "يوم واحد"
        elif days_count == 2:
            days_text = "يومان"
        elif days_count <= 10:
            days_text = f"{days_count} أيام"
        else:
            days_text = f"{days_count} يوماً"
        
        data.append({
            'اسم الموظف': result.name,
            'عدد الأيام المحولة': days_text
        })
    
    # إضافة صف الإجمالي
    if data:
        total_days = sum(result.total_days or 0 for result in results)
        if total_days == 1:
            total_text = "يوم واحد"
        elif total_days == 2:
            total_text = "يومان"
        elif total_days <= 10:
            total_text = f"{total_days} أيام"
        else:
            total_text = f"{total_days} يوماً"
            
        data.append({
            'اسم الموظف': 'الإجمالي العام',
            'عدد الأيام المحولة': total_text
        })
    
    # تحديد اسم الملف
    if start_date and end_date:
        filename = f'ملخص_المغادرات_المحولة_{start_date}_إلى_{end_date}'
    elif year:
        filename = f'ملخص_المغادرات_المحولة_{year}'
    else:
        filename = 'ملخص_المغادرات_المحولة_جميع_البيانات'
    
    return create_excel_response(data, filename)

@export.route('/directorate_employees')
@permission_required('can_export_data')
def export_directorate_employees():
    """تصدير بيانات موظفي المديرية"""
    format_type = request.args.get('format', 'excel')
    
    # الحصول على جميع موظفي المديرية
    employees = db.session.query(
        Employee.ministry_number,
        Employee.name,
        Employee.civil_id,
        Employee.gender,
        Employee.job_title,
        Employee.qualification,
        Employee.bachelor_specialization,
        Employee.high_diploma_specialization,
        Employee.masters_specialization,
        Employee.phd_specialization,
        Employee.subject,
        Employee.phone_number,
        Employee.appointment_date,
        School.name.label('school_name')
    ).join(School, Employee.school_id == School.id).filter(
        Employee.is_directorate_employee == True
    ).order_by(Employee.name).all()
    
    # إنشاء البيانات للتصدير
    data = []
    for emp in employees:
        data.append({
            'الرقم الوزاري': emp.ministry_number,
            'اسم الموظف': emp.name,
            'الرقم المدني': emp.civil_id,
            'الجنس': emp.gender,
            'الوظيفة': emp.job_title,
            'المؤهل': emp.qualification,
            'تخصص البكالوريوس': emp.bachelor_specialization or '',
            'تخصص الدبلوم العالي': emp.high_diploma_specialization or '',
            'تخصص الماجستير': emp.masters_specialization or '',
            'تخصص الدكتوراه': emp.phd_specialization or '',
            'المبحث الدراسي': emp.subject or '',
            'رقم الهاتف': emp.phone_number or '',
            'تاريخ التعيين': emp.appointment_date.strftime('%Y-%m-%d'),
            'القسم': emp.school_name
        })
    
    if format_type == 'excel':
        return create_excel_response(data, 'موظفي_المديرية')
    elif format_type == 'csv':
        return create_csv_response(data, 'موظفي_المديرية')
    elif format_type == 'pdf':
        return create_pdf_response(data, 'موظفي المديرية')
    else:
        return create_excel_response(data, 'موظفي_المديرية')

def create_csv_response(data, filename):
    """إنشاء استجابة CSV من البيانات"""
    if not data:
        data = [{'رسالة': 'لا توجد بيانات للتصدير'}]
    
    df = pd.DataFrame(data)
    output = BytesIO()
    df.to_csv(output, index=False, encoding='utf-8-sig')
    output.seek(0)
    
    response = make_response(output.read())
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    encoded_filename = quote(f'{filename}.csv', safe='')
    response.headers['Content-Disposition'] = f'attachment; filename*=UTF-8\'\'{encoded_filename}'
    
    return response

def create_pdf_response(data, filename):
    """إنشاء استجابة PDF من البيانات"""
    # للبساطة، سنعيد تحويل إلى Excel
    return create_excel_response(data, filename)

def create_excel_response(data, filename):
    """إنشاء استجابة Excel من البيانات"""
    if not data:
        # إنشاء ملف مع رسالة توضيحية
        data = [{
            'رسالة': 'لا توجد مغادرات محولة للفترة المحددة',
            'ملاحظة': 'تأكد من وجود مغادرات تم تحويلها إلى إجازات في النظام'
        }]
    
    df = pd.DataFrame(data)
    
    # إنشاء ملف Excel في الذاكرة
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='البيانات', index=False)
        
        # تنسيق الورقة
        worksheet = writer.sheets['البيانات']
        
        # تعديل عرض الأعمدة
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    output.seek(0)
    
    # إنشاء الاستجابة مع تشفير صحيح للاسم
    response = make_response(output.read())
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    
    # تشفير اسم الملف بـ UTF-8 وتحويله إلى URL encoding
    encoded_filename = quote(f'{filename}.xlsx', safe='')
    response.headers['Content-Disposition'] = f'attachment; filename*=UTF-8\'\'{encoded_filename}'
    
    return response