from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file, jsonify
from database import db
from utils import log_user_activity
from models import Employee, School, Transfer, User, FormTemplate, Leave, TechnicalDeficiency
from datetime import datetime
from sqlalchemy import func
import os
from werkzeug.utils import secure_filename
from constants import JOB_TITLES, DIRECTORATE_JOB_TITLES
from routes.auth_routes import admin_required
from io import BytesIO
import pandas as pd
from routes.auth_routes import login_required, permission_required
from sqlalchemy import or_

main = Blueprint('main', __name__)

# تحديد المجلد الذي سيتم تخزين الملفات فيه
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'forms')
# التأكد من وجود المجلد
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# أنواع الملفات المسموح بها
ALLOWED_EXTENSIONS = {'docx', 'doc', 'pdf', 'jpg', 'jpeg', 'png'}

# التحقق من امتداد الملف
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# الصفحة الرئيسية
@main.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # إحصائيات للوحة التحكم
    employees_count = Employee.query.count()
    schools_count = School.query.count()
    leaves_count = Leave.query.filter(Leave.leave_type != 'مغادرة').count()
    departures_count = Leave.query.filter_by(leave_type='مغادرة').count()
    
    # الإجازات الحالية
    today = datetime.now().date()
    current_leaves = Leave.query.filter(
        Leave.start_date <= today,
        Leave.end_date >= today,
        Leave.leave_type != 'مغادرة'
    ).join(Employee).all()
    
    return render_template('dashboard.html', 
                           employees_count=employees_count,
                           schools_count=schools_count,
                           leaves_count=leaves_count,
                           departures_count=departures_count,
                           current_leaves=current_leaves)

# نماذج المستندات
@main.route('/form_templates')
def form_templates():
    templates = FormTemplate.query.all()
    return render_template('form_templates.html', templates=templates)

# إضافة مسار لعرض قائمة النقل
# استبدال دالة transfers_list الموجودة (حوالي السطر 61)
@main.route('/transfers/list')
def transfers_list():
    # الحصول على معاملات البحث والفلترة من الطلب
    search_term = request.args.get('search', '')
    from_school_filter = request.args.get('from_school', '')
    to_school_filter = request.args.get('to_school', '')
    
    # بناء الاستعلام الأساسي
    query = Transfer.query.join(Employee)
    
    # تطبيق فلتر البحث العام (البحث الجزئي في الاسم والرقم الوزاري)
    if search_term:
        query = query.filter(
            db.or_(
                Employee.name.ilike(f'%{search_term}%'),
                Employee.ministry_number.ilike(f'%{search_term}%')
            )
        )
    
    # تطبيق فلتر المدرسة المنقول منها
    if from_school_filter:
        query = query.filter(Transfer.from_school_id == from_school_filter)
    
    # تطبيق فلتر المدرسة المنقول إليها
    if to_school_filter:
        query = query.filter(Transfer.to_school_id == to_school_filter)
    
    # تنفيذ الاستعلام وترتيب النتائج
    transfers = query.order_by(Transfer.transfer_date.desc()).all()
    
    # الحصول على قائمة المدارس للفلاتر (استثناء أقسام المديرية)
    from constants import DIRECTORATE_DEPARTMENTS
    schools = School.query.filter(~School.name.in_(DIRECTORATE_DEPARTMENTS)).order_by(School.name).all()
    
    return render_template('transfers.html', 
                         transfers=transfers, 
                         schools=schools,
                         search_term=search_term,
                         from_school_filter=from_school_filter,
                         to_school_filter=to_school_filter)

# إضافة نقل جديد
# تحديث دالة add_transfer (حوالي السطر 67)
@main.route('/transfers/add', methods=['GET', 'POST'])
def add_transfer():
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        from_school_id = request.form.get('from_school_id')
        to_school_id = request.form.get('to_school_id')
        from_job = request.form.get('from_job')
        to_job = request.form.get('to_job')
        transfer_date = datetime.strptime(request.form.get('transfer_date'), '%Y-%m-%d')
        reason = request.form.get('reason')
        
        # الحصول على بيانات الموظف
        employee = Employee.query.get(employee_id)
        
        # استخدام المبحث الدراسي للموظف
        subject = employee.subject
        
        # تحديث الموقف الفني للمدرسة المصدر
        if subject:
            from_deficiency = TechnicalDeficiency.query.filter_by(
                school_id=from_school_id,
                subject=subject,
                job_title=from_job
            ).first()
            
            if from_deficiency:
                if employee.qualification == 'بكالوريوس':
                    # إذا كان هناك زوائد، خصم من الزوائد
                    if from_deficiency.surplus_bachelor > 0:
                        from_deficiency.surplus_bachelor -= 1
                    else:
                        # إذا لم يكن هناك زوائد، زيادة النواقص
                        from_deficiency.deficiency_bachelor += 1
                elif employee.qualification == 'دبلوم عالي':
                    # إذا كان هناك زوائد، خصم من الزوائد
                    if from_deficiency.surplus_diploma > 0:
                        from_deficiency.surplus_diploma -= 1
                    else:
                        # إذا لم يكن هناك زوائد، زيادة النواقص
                        from_deficiency.deficiency_diploma += 1
                from_deficiency.updated_at = datetime.utcnow()
            else:
                # إنشاء سجل جديد للموقف الفني إذا لم يكن موجوداً
                from_deficiency = TechnicalDeficiency(
                    school_id=from_school_id,
                    specialization=subject or 'غير محدد',
                    subject=subject,
                    job_title=from_job,
                    required_count=0,
                    current_count=0,
                    deficiency_count=0,
                    deficiency_bachelor=0,
                    deficiency_diploma=0,
                    surplus_bachelor=0,
                    surplus_diploma=0
                )
                
                # تطبيق التحديث على السجل الجديد
                if employee.qualification == 'بكالوريوس':
                    from_deficiency.deficiency_bachelor = 1
                elif employee.qualification == 'دبلوم عالي':
                    from_deficiency.deficiency_diploma = 1
                
                db.session.add(from_deficiency)
            
            # تحديث الموقف الفني للمدرسة المستقبلة
            to_deficiency = TechnicalDeficiency.query.filter_by(
                school_id=to_school_id,
                subject=subject,
                job_title=to_job
            ).first()
            
            if to_deficiency:
                if employee.qualification == 'بكالوريوس':
                    # إذا كان هناك نواقص، خصم من النواقص
                    if to_deficiency.deficiency_bachelor > 0:
                        to_deficiency.deficiency_bachelor -= 1
                    else:
                        # إذا لم يكن هناك نواقص، زيادة الزوائد
                        to_deficiency.surplus_bachelor += 1
                elif employee.qualification == 'دبلوم عالي':
                    # إذا كان هناك نواقص، خصم من النواقص
                    if to_deficiency.deficiency_diploma > 0:
                        to_deficiency.deficiency_diploma -= 1
                    else:
                        # إذا لم يكن هناك نواقص، زيادة الزوائد
                        to_deficiency.surplus_diploma += 1
                to_deficiency.updated_at = datetime.utcnow()
            else:
                # إنشاء سجل جديد للموقف الفني إذا لم يكن موجوداً
                to_deficiency = TechnicalDeficiency(
                    school_id=to_school_id,
                    specialization=subject or 'غير محدد',
                    subject=subject,
                    job_title=to_job,
                    required_count=0,
                    current_count=0,
                    deficiency_count=0,
                    deficiency_bachelor=0,
                    deficiency_diploma=0,
                    surplus_bachelor=0,
                    surplus_diploma=0
                )
                
                # تطبيق التحديث على السجل الجديد
                if employee.qualification == 'بكالوريوس':
                    to_deficiency.surplus_bachelor = 1
                elif employee.qualification == 'دبلوم عالي':
                    to_deficiency.surplus_diploma = 1
                
                db.session.add(to_deficiency)
        
        # إضافة النقل إلى قاعدة البيانات
        transfer = Transfer(
            employee_id=employee_id,
            from_school_id=from_school_id,
            to_school_id=to_school_id,
            from_job=from_job,
            to_job=to_job,
            transfer_date=transfer_date,
            reason=reason
        )
        
        db.session.add(transfer)
        
        # تحديث بيانات الموظف
        employee.school_id = to_school_id
        employee.job_title = to_job
        
        db.session.commit()
        
        # تسجيل العملية في سجلات المستخدمين
        from_school = School.query.get(from_school_id)
        to_school = School.query.get(to_school_id)
        log_user_activity(
            user_id=session.get('user_id'),
            action='إضافة',
            module='النقل',
            description=f'تم تسجيل نقل الموظف: {employee.name} من {from_school.name} إلى {to_school.name}',
            target_id=transfer.id,
            target_type='نقل'
        )
        
        flash('تم تسجيل النقل بنجاح وتحديث الموقف الفني', 'success')
        return redirect(url_for('main.transfers_list'))
    
    # الحصول على قائمة الموظفين والمدارس (استثناء أقسام المديرية)
    employees = Employee.query.filter_by(is_directorate_employee=False).order_by(Employee.name).all()
    from constants import DIRECTORATE_DEPARTMENTS
    schools = School.query.filter(~School.name.in_(DIRECTORATE_DEPARTMENTS)).order_by(School.name).all()
    
    return render_template('transfer_form.html', employees=employees, schools=schools)

# تنزيل النموذج
@main.route('/form_templates/download/<int:id>')
def download_form_template(id):
    template = FormTemplate.query.get_or_404(id)
    file_path = os.path.join(UPLOAD_FOLDER, template.file_path)
    
    # التحقق من وجود الملف
    if not os.path.exists(file_path):
        flash('الملف غير موجود', 'danger')
        return redirect(url_for('main.form_templates'))
    
    # استخداة الامتداد الأصلي المحفوظ في قاعدة البيانات
    original_extension = template.original_extension or ''
    
    # إنشاء اسم التنزيل مع الامتداد الأصلي
    if original_extension:
        download_filename = f"{template.name}.{original_extension}"
    else:
        # في حالة عدم وجود امتداد محفوظ، استخراجه من اسم الملف
        stored_filename = template.file_path
        if '_' in stored_filename:
            parts = stored_filename.split('_', 2)
            if len(parts) >= 3:
                original_filename_with_ext = parts[2]
            else:
                original_filename_with_ext = stored_filename
        else:
            original_filename_with_ext = stored_filename
        
        if '.' in original_filename_with_ext:
            original_extension = original_filename_with_ext.rsplit('.', 1)[1].lower()
            download_filename = f"{template.name}.{original_extension}"
        else:
            download_filename = template.name
    
    # تحديق نوع MIME بناءً على الامتداد
    mimetype_map = {
        'pdf': 'application/pdf',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'doc': 'application/msword',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'xls': 'application/vnd.ms-excel',
        'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'ppt': 'application/vnd.ms-powerpoint',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'txt': 'text/plain',
        'rtf': 'application/rtf'
    }
    
    mimetype = mimetype_map.get(original_extension, 'application/octet-stream')
    
    return send_file(file_path, mimetype=mimetype, as_attachment=True, download_name=download_filename)

# مسارات إعادة التوجيه (واحد فقط لكل مسار)
# Remove this conflicting route - it conflicts with school.schools route
# @main.route('/schools')
# def redirect_to_schools():
#     return redirect(url_for('school.schools'))

# Remove or comment out this route
# @main.route('/directorate_employees')
# def redirect_to_directorate_employees():
#     return redirect(url_for('employee.directorate_employees'))

# Remove or comment out these routes
# @main.route('/employees')
# def redirect_to_employees():
#     return redirect(url_for('employee.employees'))

# @main.route('/employees/add')
# def add_employee_redirect():
#     return redirect(url_for('employee.add_employee'))
# Remove or comment out this route
# @main.route('/leaves')
# def redirect_to_leaves():
#     return redirect(url_for('leave.leaves'))

# Remove or comment out this route
# @main.route('/schools/add')
# def add_school_redirect():
#     return redirect(url_for('school.add_school'))

# رصيد الإجازات
# احذف هذه الوظائف:
# @main.route('/leave_balances')
# def leave_balances():
#     ...

# @main.route('/export_leave_balances_data')
# def export_leave_balances_data():
#     ...

@main.route('/download_import_template')
def download_import_template():
    # تحديد ما إذا كان النموذج لموظفي المديرية
    is_directorate = request.args.get('is_directorate') == 'true'
    
    # إنشاء نموذج شامل مع أمثلة متعددة
    data = {
        'الرقم الوزاري': ['EMP001', 'EMP002', 'EMP003', 'EMP004', 'EMP005'],
        'الاسم': ['أحمد محمد علي', 'فاطمة أحمد محمد', 'محمد علي حسن', 'سارة خالد أحمد', 'عمر يوسف محمود'],
        'الرقم المدني': ['12345678901', '12345678902', '12345678903', '12345678904', '12345678905'],
        'الجنس': ['ذكر', 'أنثى', 'ذكر', 'أنثى', 'ذكر'],
        'الوظيفة': ['معلم', 'معلمة', 'مدير', 'مشرفة تربوية', 'مساعد إداري'],
        'المؤهل': ['بكالوريوس', 'ماجستير', 'بكالوريوس', 'دكتوراه', 'دبلوم عالي'],
        'تخصص بكالوريوس': ['رياضيات', 'لغة عربية', 'إدارة تربوية', 'علوم', 'حاسوب'],
        'تخصص دبلوم العالي': ['', 'تكنولوجيا التعليم', '', '', 'إدارة تعليمية'],
        'تخصص ماجستير': ['', 'مناهج وطرق تدريس', '', 'تقنيات تعليم', ''],
        'تخصص دكتوراه': ['', '', '', 'فلسفة التربية', ''],
        'المبحث الدراسي': ['الرياضيات', 'اللغة العربية', 'إدارة', 'العلوم', 'الحاسوب'],
        'رقم الهاتف': ['0501234567', '0507654321', '0509876543', '0501122334', '0509988776'],
        'تاريخ التعيين': ['2023-01-01', '15/03/2022', '2021-09-01', '01-05-2020', '2019/12/15'],
    }
    
    # تحديد المدارس/الأقسام حسب نوع الموظفين
    if is_directorate:
        # الحصول على أقسام المديرية من قاعدة البيانات
        from constants import DIRECTORATE_DEPARTMENTS
        departments = []
        for dept in DIRECTORATE_DEPARTMENTS:
            school = School.query.filter_by(name=dept).first()
            if school:
                departments.append(school.name)
        
        # إذا لم يتم العثور على أقسام، استخدم القيم الافتراضية
        if not departments:
            departments = ['قسم شؤون الموظفين', 'قسم التخطيط', 'قسم الإشراف التربوي', 'قسم الامتحانات', 'قسم التعليم المهني']
        
        # تأكد من أن لدينا ما يكفي من الأقسام للأمثلة
        while len(departments) < 5:
            departments.append(departments[0])
        
        data['اسم القسم'] = departments[:5]
    else:
        # الحصول على المدارس من قاعدة البيانات (استبعاد أقسام المديرية)
        from constants import DIRECTORATE_DEPARTMENTS
        schools_query = School.query.filter(~School.name.in_(DIRECTORATE_DEPARTMENTS)).order_by(School.name).limit(5).all()
        
        # إذا لم يتم العثور على مدارس، استخدم القيم الافتراضية
        if not schools_query:
            schools = ['مدرسة الأمل الابتدائية', 'مدرسة النور الثانوية للبنات', 'مدرسة الفجر الأساسية', 'مدرسة الزهراء الثانوية', 'مدرسة الرازي الأساسية']
        else:
            schools = [school.name for school in schools_query]
        
        # تأكد من أن لدينا ما يكفي من المدارس للأمثلة
        while len(schools) < 5:
            schools.append(schools[0])
        
        data['اسم المدرسة'] = schools[:5]
    
    # إنشاء DataFrame
    df = pd.DataFrame(data)
    
    # تصدير إلى ملف Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='بيانات الموظفين')
        
        # الحصول على ورقة العمل وكائن الكتاب
        workbook = writer.book
        worksheet = writer.sheets['بيانات الموظفين']
        worksheet.right_to_left()
        
        # تنسيق العناوين
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1,
            'align': 'center'
        })
        
        # تطبيق التنسيق على العناوين
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # تعيين عرض الأعمدة
        for idx, col in enumerate(df.columns):
            max_len = max(df[col].astype(str).apply(len).max(), len(str(col)) + 2)
            worksheet.set_column(idx, idx, max_len)
        
        # إضافة ورقة تعليمات
        instructions_sheet = workbook.add_worksheet('تعليمات الاستيراد')
        instructions_sheet.right_to_left()
        
        # تنسيق العناوين في ورقة التعليمات
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#4472C4',
            'font_color': 'white'
        })
        
        subtitle_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'align': 'right',
            'valign': 'vcenter',
            'fg_color': '#D7E4BC'
        })
        
        text_format = workbook.add_format({
            'align': 'right',
            'valign': 'vcenter',
            'text_wrap': True
        })
        
        # إضافة محتوى ورقة التعليمات
        instructions_sheet.merge_range('A1:F1', 'تعليمات استيراد بيانات الموظفين', title_format)
        instructions_sheet.set_row(0, 30)
        
        instructions_sheet.merge_range('A3:F3', 'الحقول الإلزامية', subtitle_format)
        instructions_sheet.merge_range('A4:F4', 'الحقول التالية إلزامية ويجب تعبئتها لكل موظف: الرقم الوزاري، الاسم، الرقم المدني، الوظيفة، ' + ('اسم القسم' if is_directorate else 'اسم المدرسة'), text_format)
        
        instructions_sheet.merge_range('A6:F6', 'تنسيقات التاريخ المدعومة', subtitle_format)
        instructions_sheet.merge_range('A7:F7', 'يمكن استخدام أي من التنسيقات التالية: YYYY-MM-DD (مثل 2023-01-15)، DD/MM/YYYY (مثل 15/01/2023)، DD-MM-YYYY (مثل 15-01-2023)', text_format)
        
        instructions_sheet.merge_range('A9:F9', 'أسماء الأقسام/المدارس', subtitle_format)
        instructions_sheet.merge_range('A10:F10', 'يدعم النظام المطابقة التقريبية لأسماء الأقسام/المدارس، لكن يفضل استخدام الأسماء الدقيقة المسجلة في النظام', text_format)
        
        instructions_sheet.merge_range('A12:F12', 'نصائح لتجنب الأخطاء', subtitle_format)
        instructions_sheet.merge_range('A13:F13', '1. تأكد من عدم وجود مسافات زائدة في بداية أو نهاية البيانات', text_format)
        instructions_sheet.merge_range('A14:F14', '2. تأكد من أن الرقم الوزاري والرقم المدني فريدان لكل موظف', text_format)
        instructions_sheet.merge_range('A15:F15', '3. تأكد من أن جميع البيانات الإلزامية مكتملة', text_format)
        
        # تعديل عرض الأعمدة في ورقة التعليمات
        instructions_sheet.set_column('A:F', 20)
    
    output.seek(0)
    
    # تحديد اسم الملف حسب نوع الموظفين
    if is_directorate:
        filename = 'نموذج_بيانات_موظفي_المديرية.xlsx'
    else:
        filename = 'نموذج_بيانات_الموظفين.xlsx'
    
    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

def parse_date_flexible(date_str):
    """
    تحليل التاريخ بتنسيقات مختلفة
    يدعم التنسيقات التالية:
    - YYYY-MM-DD
    - DD/MM/YYYY
    - DD-MM-YYYY
    - MM/DD/YYYY
    - التنسيقات العربية
    """
    if not date_str or pd.isna(date_str):
        return None
    
    # تنظيف سلسلة التاريخ
    date_str = str(date_str).strip()
    
    # قائمة تنسيقات التاريخ المدعومة
    date_formats = [
        '%Y-%m-%d',  # YYYY-MM-DD
        '%d/%m/%Y',  # DD/MM/YYYY
        '%d-%m-%Y',  # DD-MM-YYYY
        '%m/%d/%Y',  # MM/DD/YYYY
        '%Y/%m/%d',  # YYYY/MM/DD
        '%d.%m.%Y',  # DD.MM.YYYY
        '%Y.%m.%d',  # YYYY.MM.DD
    ]
    
    # محاولة تحليل التاريخ باستخدام التنسيقات المختلفة
    for date_format in date_formats:
        try:
            return datetime.strptime(date_str, date_format).date()
        except ValueError:
            continue
    
    # محاولة استخراج التاريخ من النص
    try:
        # تحويل الأرقام العربية إلى إنجليزية إذا وجدت
        arabic_to_english = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')
        date_str = date_str.translate(arabic_to_english)
        
        # استخراج الأرقام من النص
        import re
        numbers = re.findall(r'\d+', date_str)
        
        if len(numbers) >= 3:
            # تخمين ترتيب التاريخ بناءً على القيم
            year = None
            month = None
            day = None
            
            for num in numbers:
                if len(num) == 4 and 1900 <= int(num) <= 2100:
                    year = int(num)
                elif int(num) > 31:
                    year = int(num)
                elif int(num) > 12:
                    day = int(num)
                else:
                    if month is None:
                        month = int(num)
                    else:
                        day = int(num)
            
            # التحقق من وجود جميع مكونات التاريخ
            if year and month and day:
                # التحقق من صحة التاريخ
                if 1 <= month <= 12 and 1 <= day <= 31:
                    return datetime(year, month, day).date()
    except:
        pass
    
    # إذا فشلت جميع المحاولات
    raise ValueError(f'تنسيق التاريخ غير مدعوم: {date_str}')

# تحديث دالة import_employees_data لاستخدام الدالة الجديدة
@main.route('/import_employees_data', methods=['POST'])
@permission_required('can_manage_employees')
def import_employees_data():
    from constants import DIRECTORATE_DEPARTMENTS
    
    if 'importFile' not in request.files:
        flash('لم يتم اختيار ملف', 'danger')
        return redirect(url_for('employee.export_employees'))
    
    file = request.files['importFile']
    if file.filename == '':
        flash('لم يتم اختيار ملف', 'danger')
        return redirect(url_for('employee.export_employees'))
    
    # تحديد ما إذا كان الاستيراد لموظفي المديرية
    is_directorate = request.form.get('is_directorate') == 'true'
    
    try:
        # Read the uploaded file
        if file.filename.endswith('.xlsx') or file.filename.endswith('.xls'):
            df = pd.read_excel(file)
        elif file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            flash('نوع الملف غير مدعوم. يرجى استخدام Excel أو CSV', 'danger')
            if is_directorate:
                return redirect(url_for('employee.directorate_employees'))
            else:
                return redirect(url_for('employee.export_employees'))
        
        # تنظيف أسماء الأعمدة من المسافات الزائدة
        df.columns = [col.strip() if isinstance(col, str) else col for col in df.columns]
        
        # Process the data and add employees
        added = 0
        updated = 0
        skipped = 0
        errors = []
        
        # تحديد اسم العمود بناءً على نوع الاستيراد
        department_column = 'اسم القسم' if is_directorate else 'اسم المدرسة'
        
        # التحقق من وجود الأعمدة المطلوبة
        required_columns = ['الرقم الوزاري', 'الاسم', 'الرقم المدني', 'الوظيفة', department_column]
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            error_msg = f'الأعمدة التالية مطلوبة وغير موجودة في الملف: {", ".join(missing_columns)}'
            flash(error_msg, 'danger')
            session['import_results'] = {
                'added': 0,
                'updated': 0,
                'skipped': 0,
                'errors': [error_msg]
            }
            if is_directorate:
                return redirect(url_for('employee.directorate_employees'))
            else:
                return redirect(url_for('employee.export_employees'))
        
        # الحصول على قائمة الأقسام/المدارس من قاعدة البيانات
        all_schools = School.query.all()
        school_names = {school.name.strip(): school for school in all_schools}
        
        # إنشاء قاموس للأقسام/المدارس المتشابهة
        similar_schools = {}
        for name in school_names:
            # إزالة أل التعريف والمسافات الزائدة للمقارنة
            clean_name = name.replace('ال', '').replace(' ', '').strip()
            similar_schools[clean_name] = school_names[name]
        
        # تحويل أسماء أقسام المديرية إلى قائمة نظيفة للمقارنة
        directorate_dept_clean = [dept.replace('ال', '').replace(' ', '').strip() for dept in DIRECTORATE_DEPARTMENTS]
        
        for index, row in df.iterrows():
            try:
                # التأكد من أن جميع القيم هي نصوص وإزالة المسافات الزائدة
                row_dict = {}
                for col in df.columns:
                    if col in row and not pd.isna(row[col]):
                        if isinstance(row[col], str):
                            row_dict[col] = row[col].strip()
                        else:
                            row_dict[col] = row[col]
                    else:
                        row_dict[col] = None
                
                # التحقق من البيانات الإلزامية
                required_fields = ['الرقم الوزاري', 'الاسم', 'الرقم المدني', 'الوظيفة', department_column]
                missing_fields = [field for field in required_fields if field not in row_dict or row_dict[field] is None]
                
                if missing_fields:
                    errors.append(f'الصف {index + 2}: بيانات إلزامية مفقودة: {", ".join(missing_fields)}')
                    skipped += 1
                    continue
                
                # البحث عن المدرسة/القسم باستخدام المطابقة التقريبية
                school = None
                dept_name = row_dict[department_column]
                
                # البحث المباشر
                if dept_name in school_names:
                    school = school_names[dept_name]
                else:
                    # تنظيف اسم القسم/المدرسة للمقارنة التقريبية
                    clean_dept_name = dept_name.replace('ال', '').replace(' ', '').strip()
                    
                    # البحث في الأسماء المتشابهة
                    if clean_dept_name in similar_schools:
                        school = similar_schools[clean_dept_name]
                    else:
                        # البحث عن أقرب تطابق
                        for name, school_obj in school_names.items():
                            clean_name = name.replace('ال', '').replace(' ', '').strip()
                            if clean_dept_name in clean_name or clean_name in clean_dept_name:
                                school = school_obj
                                break
                
                if not school:
                    # إنشاء قسم/مدرسة جديدة إذا كان الاستيراد لموظفي المديرية وكان القسم موجودا في القائمة
                    clean_dept_name = dept_name.replace('ال', '').replace(' ', '').strip()
                    if is_directorate and (dept_name in DIRECTORATE_DEPARTMENTS or clean_dept_name in directorate_dept_clean):
                        school = School(name=dept_name, region="المديرية")
                        db.session.add(school)
                        db.session.flush()  # للحصول على ID
                        school_names[dept_name] = school
                        similar_schools[clean_dept_name] = school
                    else:
                        errors.append(f'الصف {index + 2}: المدرسة/القسم غير موجود: {dept_name}')
                        skipped += 1
                        continue
                
                # التحقق من أن المدرسة/القسم يتوافق مع نوع الموظف (مديرية/مدرسة)
                clean_school_name = school.name.replace('ال', '').replace(' ', '').strip()
                is_school_directorate = school.name in DIRECTORATE_DEPARTMENTS or clean_school_name in directorate_dept_clean
                
                if is_directorate != is_school_directorate:
                    if is_directorate:
                        errors.append(f'الصف {index + 2}: القسم المحدد "{school.name}" ليس من أقسام المديرية')
                    else:
                        errors.append(f'الصف {index + 2}: المدرسة المحددة "{school.name}" هي قسم مديرية')
                    skipped += 1
                    continue
                
                # تنظيف الرقم الوزاري والرقم المدني
                ministry_number = str(row_dict['الرقم الوزاري']).strip()
                civil_id = str(row_dict['الرقم المدني']).strip()
                
                # البحث عن الموظف الحالي
                existing_employee = Employee.query.filter(
                    db.or_(
                        Employee.ministry_number == ministry_number,
                        Employee.civil_id == civil_id
                    )
                ).first()
                
                # تحضير البيانات المشتركة
                employee_data = {
                    'name': row_dict['الاسم'],
                    'ministry_number': ministry_number,
                    'civil_id': civil_id,
                    'job_title': row_dict['الوظيفة'],
                    'school_id': school.id,
                    'phone_number': str(row_dict.get('رقم الهاتف', '')) if row_dict.get('رقم الهاتف') else None,
                    'gender': row_dict.get('الجنس', 'ذكر'),
                    'qualification': row_dict.get('المؤهل', ''),
                    'bachelor_specialization': row_dict.get('تخصص بكالوريوس', ''),
                    'high_diploma_specialization': row_dict.get('تخصص دبلوم العالي', ''),
                    'masters_specialization': row_dict.get('تخصص ماجستير', ''),
                    'phd_specialization': row_dict.get('تخصص دكتوراه', ''),
                    'subject': row_dict.get('المبحث الدراسي', ''),
                    'is_directorate_employee': is_directorate
                }
                
                # معالجة تاريخ التعيين
                if row_dict.get('تاريخ التعيين'):
                    try:
                        # محاولة تحويل التاريخ بالتنسيقات المختلفة
                        appointment_date = parse_date_flexible(str(row_dict['تاريخ التعيين']))
                        if appointment_date:
                            employee_data['appointment_date'] = appointment_date
                    except Exception as e:
                        errors.append(f'الصف {index + 2}: خطأ في تنسيق التاريخ: {str(e)}')
                
                if existing_employee:
                    # تحديث الموظف الحالي
                    for key, value in employee_data.items():
                        setattr(existing_employee, key, value)
                    updated += 1
                else:
                    # إنشاء موظف جديد
                    new_employee = Employee(**employee_data)
                    db.session.add(new_employee)
                    added += 1
                    
            except Exception as e:
                errors.append(f'خطأ في الصف {index + 2}: {str(e)}')
                skipped += 1
        
        db.session.commit()
        
        # Store results in session for display - only if there are results to show
        if added > 0 or updated > 0 or skipped > 0 or errors:
            session['import_results'] = {
                'added': added,
                'updated': updated,
                'skipped': skipped,
                'errors': errors
            }
        
        flash(f'تم استيراد البيانات بنجاح. تمت إضافة {added} موظف وتحديث {updated} موظف', 'success')
        
    except Exception as e:
        flash(f'خطأ في قراءة الملف: {str(e)}', 'danger')
        session['import_results'] = {
            'added': 0,
            'updated': 0,
            'skipped': 0,
            'errors': [f'خطأ في قراءة الملف: {str(e)}']
        }
    
    # تحديد صفحة العودة بناءً على نوع الموظفين
    if is_directorate:
        return redirect(url_for('employee.directorate_employees'))
    else:
        return redirect(url_for('employee.export_employees'))

# النسخ الاحتياطي التلقائي باستخدام Windows Task Scheduler:
# 1. افتح Task Scheduler من قائمة Start
# 2. انقر على Create Basic Task
# 3. ادخل اسم المهمة: Database Backup
# 4. اختر التكرار (يومي، اسبوعي، الخ)
# 5. حدد الوقت المناسب
# 6. اختر Start a program
# 7. في Program/script: python
# 8. في Arguments: backup_database.py
# 9. في Start in: c:\Users\almshagba\Desktop\wael _pro

# أو استخدام ملف batch:
# في Program/script: c:\Users\almshagba\Desktop\wael _pro\backup_daily.bat

@main.route('/backup_database')
@permission_required('can_backup_database')
def backup_database_route():
    import shutil
    import os
    from datetime import datetime
    
    try:
        # إنشاء مجلد النسخ الاحتياطية
        backup_dir = 'backups'
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        # إنشاء اسم الملف مع التاريخ
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        backup_filename = f'employees_backup_{timestamp}.db'
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # نسخ قاعدة البيانات
        shutil.copy2('instance/employees.db', backup_path)
        
        flash(f'تم إنشاء النسخة الاحتياطية بنجاح: {backup_filename}', 'success')
        
    except Exception as e:
        flash(f'خطأ في إنشاء النسخة الاحتياطية: {str(e)}', 'danger')
    
    return redirect(url_for('main.index'))

# Add this route after the add_form_template route
@main.route('/form_templates/delete/<int:id>', methods=['POST'])
@permission_required('can_manage_forms')
def delete_form_template(id):
    template = FormTemplate.query.get_or_404(id)
    
    try:
        # حذف الملف من النظام
        if os.path.exists(template.file_path):
            os.remove(template.file_path)
        
        # حذف السجل من قاعدة البيانات
        db.session.delete(template)
        db.session.commit()
        
        flash('تم حذف النموذج بنجاح', 'success')
    except Exception as e:
        flash(f'حدث خطأ أثناء حذف النموذج: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('main.form_templates'))

@main.route('/form_templates/add', methods=['GET', 'POST'])
# استبدال @admin_required بـ:
@permission_required('can_manage_forms')  # للنماذج
# أو
@permission_required('can_process_monthly_departures')  # للمغادرات الشهرية
def add_form_template():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        file_type = request.form.get('file_type')
        
        # التحقق من وجود الملف
        if 'file' not in request.files:
            flash('لم يتم اختيار ملف', 'error')
            return render_template('form_template_form.html')
        
        file = request.files['file']
        if file.filename == '':
            flash('لم يتم اختيار ملف', 'error')
            return render_template('form_template_form.html')
        
        if file and allowed_file(file.filename):
            # حفظ الامتداد الأصلي
            original_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
            
            # إنشاء اسم ملف آمن
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            
            try:
                # حفظ الملف
                file.save(file_path)
                
                # إضافة النموذج إلى قاعدة البيانات
                template = FormTemplate(
                    name=name,
                    file_path=file_path,
                    file_type=file_type,
                    description=description,
                    user_id=session['user_id'],
                    original_extension=original_extension
                )
                
                db.session.add(template)
                db.session.commit()
                
                flash('تم إضافة النموذج بنجاح', 'success')
                return redirect(url_for('main.form_templates'))
                
            except Exception as e:
                flash(f'حدث خطأ أثناء حفظ الملف: {str(e)}', 'error')
                return render_template('form_template_form.html')
        else:
            flash('نوع الملف غير مسموح', 'error')
            return render_template('form_template_form.html')
    
    return render_template('form_template_form.html')

# إضافة مسار تعديل النقل
@main.route('/transfers/edit/<int:id>', methods=['GET', 'POST'])
def edit_transfer(id):
    transfer = Transfer.query.get_or_404(id)
    
    if request.method == 'POST':
        # حفظ البيانات القديمة للتراجع عن التحديث في الموقف الفني
        old_from_school_id = transfer.from_school_id
        old_to_school_id = transfer.to_school_id
        old_from_job = transfer.from_job
        old_to_job = transfer.to_job
        
        # الحصول على بيانات الموظف
        employee = Employee.query.get(transfer.employee_id)
        
        # استخدام المبحث الدراسي للموظف
        subject = employee.subject
        
        # التراجع عن التحديث السابق في الموقف الفني
        if subject:
            # إعادة تعيين الموقف الفني للمدرسة المصدر القديمة
            old_from_deficiency = TechnicalDeficiency.query.filter_by(
                school_id=old_from_school_id,
                subject=subject,
                job_title=old_from_job
            ).first()
            
            if old_from_deficiency:
                if employee.qualification == 'بكالوريوس':
                    # إذا كان هناك نواقص، خصم من النواقص
                    if old_from_deficiency.deficiency_bachelor > 0:
                        old_from_deficiency.deficiency_bachelor -= 1
                    else:
                        # إذا لم يكن هناك نواقص، زيادة الزوائد
                        old_from_deficiency.surplus_bachelor += 1
                elif employee.qualification == 'دبلوم عالي':
                    # إذا كان هناك نواقص، خصم من النواقص
                    if old_from_deficiency.deficiency_diploma > 0:
                        old_from_deficiency.deficiency_diploma -= 1
                    else:
                        # إذا لم يكن هناك نواقص، زيادة الزوائد
                        old_from_deficiency.surplus_diploma += 1
                old_from_deficiency.updated_at = datetime.utcnow()
            
            # إعادة تعيين الموقف الفني للمدرسة المستقبلة القديمة
            old_to_deficiency = TechnicalDeficiency.query.filter_by(
                school_id=old_to_school_id,
                subject=subject,
                job_title=old_to_job
            ).first()
            
            if old_to_deficiency:
                if employee.qualification == 'بكالوريوس':
                    # إذا كان هناك زوائد، خصم من الزوائد
                    if old_to_deficiency.surplus_bachelor > 0:
                        old_to_deficiency.surplus_bachelor -= 1
                    else:
                        # إذا لم يكن هناك زوائد، زيادة النواقص
                        old_to_deficiency.deficiency_bachelor += 1
                elif employee.qualification == 'دبلوم عالي':
                    # إذا كان هناك زوائد، خصم من الزوائد
                    if old_to_deficiency.surplus_diploma > 0:
                        old_to_deficiency.surplus_diploma -= 1
                    else:
                        # إذا لم يكن هناك زوائد، زيادة النواقص
                        old_to_deficiency.deficiency_diploma += 1
                old_to_deficiency.updated_at = datetime.utcnow()
        
        # تحديث بيانات النقل
        transfer.employee_id = request.form.get('employee_id')
        transfer.from_school_id = request.form.get('from_school_id')
        transfer.to_school_id = request.form.get('to_school_id')
        transfer.from_job = request.form.get('from_job')
        transfer.to_job = request.form.get('to_job')
        transfer.transfer_date = datetime.strptime(request.form.get('transfer_date'), '%Y-%m-%d')
        transfer.reason = request.form.get('reason')
        
        # تطبيق التحديث الجديد في الموقف الفني
        if subject:
            # تحديث الموقف الفني للمدرسة المصدر الجديدة
            new_from_deficiency = TechnicalDeficiency.query.filter_by(
                school_id=transfer.from_school_id,
                subject=subject,
                job_title=transfer.from_job
            ).first()
            
            if new_from_deficiency:
                if employee.qualification == 'بكالوريوس':
                    # إذا كان هناك زوائد، خصم من الزوائد
                    if new_from_deficiency.surplus_bachelor > 0:
                        new_from_deficiency.surplus_bachelor -= 1
                    else:
                        # إذا لم يكن هناك زوائد، زيادة النواقص
                        new_from_deficiency.deficiency_bachelor += 1
                elif employee.qualification == 'دبلوم عالي':
                    # إذا كان هناك زوائد، خصم من الزوائد
                    if new_from_deficiency.surplus_diploma > 0:
                        new_from_deficiency.surplus_diploma -= 1
                    else:
                        # إذا لم يكن هناك زوائد، زيادة النواقص
                        new_from_deficiency.deficiency_diploma += 1
                new_from_deficiency.updated_at = datetime.utcnow()
            else:
                # إنشاء سجل جديد للموقف الفني إذا لم يكن موجوداً
                new_from_deficiency = TechnicalDeficiency(
                    school_id=transfer.from_school_id,
                    specialization=subject or 'غير محدد',
                    subject=subject,
                    job_title=transfer.from_job,
                    required_count=0,
                    current_count=0,
                    deficiency_count=0,
                    deficiency_bachelor=0,
                    deficiency_diploma=0,
                    surplus_bachelor=0,
                    surplus_diploma=0
                )
                
                # تطبيق التحديث على السجل الجديد
                if employee.qualification == 'بكالوريوس':
                    new_from_deficiency.deficiency_bachelor = 1
                elif employee.qualification == 'دبلوم عالي':
                    new_from_deficiency.deficiency_diploma = 1
                
                db.session.add(new_from_deficiency)
            
            # تحديث الموقف الفني للمدرسة المستقبلة الجديدة
            new_to_deficiency = TechnicalDeficiency.query.filter_by(
                school_id=transfer.to_school_id,
                subject=subject,
                job_title=transfer.to_job
            ).first()
            
            if new_to_deficiency:
                if employee.qualification == 'بكالوريوس':
                    # إذا كان هناك نواقص، خصم من النواقص
                    if new_to_deficiency.deficiency_bachelor > 0:
                        new_to_deficiency.deficiency_bachelor -= 1
                    else:
                        # إذا لم يكن هناك نواقص، زيادة الزوائد
                        new_to_deficiency.surplus_bachelor += 1
                elif employee.qualification == 'دبلوم عالي':
                    # إذا كان هناك نواقص، خصم من النواقص
                    if new_to_deficiency.deficiency_diploma > 0:
                        new_to_deficiency.deficiency_diploma -= 1
                    else:
                        # إذا لم يكن هناك نواقص، زيادة الزوائد
                        new_to_deficiency.surplus_diploma += 1
                new_to_deficiency.updated_at = datetime.utcnow()
            else:
                # إنشاء سجل جديد للموقف الفني إذا لم يكن موجوداً
                new_to_deficiency = TechnicalDeficiency(
                    school_id=transfer.to_school_id,
                    specialization=subject or 'غير محدد',
                    subject=subject,
                    job_title=transfer.to_job,
                    required_count=0,
                    current_count=0,
                    deficiency_count=0,
                    deficiency_bachelor=0,
                    deficiency_diploma=0,
                    surplus_bachelor=0,
                    surplus_diploma=0
                )
                
                # تطبيق التحديث على السجل الجديد
                if employee.qualification == 'بكالوريوس':
                    new_to_deficiency.surplus_bachelor = 1
                elif employee.qualification == 'دبلوم عالي':
                    new_to_deficiency.surplus_diploma = 1
                
                db.session.add(new_to_deficiency)
        
        # تحديث بيانات الموظف
        employee = Employee.query.get(transfer.employee_id)
        employee.school_id = transfer.to_school_id
        employee.job_title = transfer.to_job
        
        db.session.commit()
        flash('تم تحديث النقل بنجاح وتحديث الموقف الفني', 'success')
        return redirect(url_for('main.transfers_list'))
    
    # الحصول على قائمة الموظفين والمدارس (استثناء أقسام المديرية)
    employees = Employee.query.filter_by(is_directorate_employee=False).order_by(Employee.name).all()
    from constants import DIRECTORATE_DEPARTMENTS
    schools = School.query.filter(~School.name.in_(DIRECTORATE_DEPARTMENTS)).order_by(School.name).all()
    
    return render_template('transfer_form.html', 
                         employees=employees, 
                         schools=schools, 
                         transfer=transfer, 
                         edit_mode=True)

# إضافة مسار حذف النقل
@main.route('/transfers/delete/<int:id>', methods=['POST'])
def delete_transfer(id):
    transfer = Transfer.query.get_or_404(id)
    
    # الحصول على بيانات الموظف قبل حذف النقل
    employee = Employee.query.get(transfer.employee_id)
    
    # استخدام المبحث من بيانات الموظف
    subject = employee.subject
    
    # التراجع عن تأثير النقل على الموقف الفني
    if subject:
        # إعادة تعيين الموقف الفني للمدرسة المصدر
        from_deficiency = TechnicalDeficiency.query.filter_by(
            school_id=transfer.from_school_id,
            subject=subject,
            job_title=transfer.from_job
        ).first()
        
        if from_deficiency:
            if employee.qualification == 'بكالوريوس':
                # إذا كان هناك نواقص، خصم من النواقص
                if from_deficiency.deficiency_bachelor > 0:
                    from_deficiency.deficiency_bachelor -= 1
                else:
                    # إذا لم يكن هناك نواقص، زيادة الزوائد
                    from_deficiency.surplus_bachelor += 1
            elif employee.qualification == 'دبلوم عالي':
                # إذا كان هناك نواقص، خصم من النواقص
                if from_deficiency.deficiency_diploma > 0:
                    from_deficiency.deficiency_diploma -= 1
                else:
                    # إذا لم يكن هناك نواقص، زيادة الزوائد
                    from_deficiency.surplus_diploma += 1
            from_deficiency.updated_at = datetime.utcnow()
        
        # إعادة تعيين الموقف الفني للمدرسة المستقبلة
        to_deficiency = TechnicalDeficiency.query.filter_by(
            school_id=transfer.to_school_id,
            subject=subject,
            job_title=transfer.to_job
        ).first()
        
        if to_deficiency:
            if employee.qualification == 'بكالوريوس':
                # إذا كان هناك زوائد، خصم من الزوائد
                if to_deficiency.surplus_bachelor > 0:
                    to_deficiency.surplus_bachelor -= 1
                else:
                    # إذا لم يكن هناك زوائد، زيادة النواقص
                    to_deficiency.deficiency_bachelor += 1
            elif employee.qualification == 'دبلوم عالي':
                # إذا كان هناك زوائد، خصم من الزوائد
                if to_deficiency.surplus_diploma > 0:
                    to_deficiency.surplus_diploma -= 1
                else:
                    # إذا لم يكن هناك زوائد، زيادة النواقص
                    to_deficiency.deficiency_diploma += 1
            to_deficiency.updated_at = datetime.utcnow()
    
    # البحث عن النقلات المتبقية قبل حذف النقل الحالي
    remaining_transfers = Transfer.query.filter(
        Transfer.employee_id == employee.id,
        Transfer.id != transfer.id
    ).order_by(Transfer.transfer_date.desc()).all()
    
    # حفظ بيانات النقل قبل الحذف للتسجيل
    employee_name = employee.name
    from_school = School.query.get(transfer.from_school_id)
    to_school = School.query.get(transfer.to_school_id)
    transfer_id = transfer.id
    
    # حذف سجل النقل
    db.session.delete(transfer)
    
    if remaining_transfers:
        # تحديث بيانات الموظف بناءً على آخر نقل متبقي
        last_remaining_transfer = remaining_transfers[0]
        employee.school_id = last_remaining_transfer.to_school_id
        employee.job_title = last_remaining_transfer.to_job
    else:
        # إذا لم يكن هناك نقل آخر، إعادة الموظف إلى مدرسته الأصلية
        # استخدام بيانات النقل المحذوف لتحديد المدرسة الأصلية
        employee.school_id = transfer.from_school_id
        employee.job_title = transfer.from_job
    
    db.session.commit()
    
    # تسجيل العملية في سجلات المستخدمين
    log_user_activity(
        user_id=session.get('user_id'),
        action='حذف',
        module='النقل',
        description=f'تم حذف نقل الموظف: {employee_name} من {from_school.name} إلى {to_school.name}',
        target_id=transfer_id,
        target_type='نقل'
    )
    
    flash('تم حذف سجل النقل بنجاح وتحديث الموقف الفني', 'success')
    return redirect(url_for('main.transfers_list'))

# إضافة مسار طباعة النقل الفردي
@main.route('/transfers/print/<int:id>')
def print_transfer(id):
    transfer = Transfer.query.get_or_404(id)
    return render_template('print_transfer.html', transfer=transfer)

@main.route('/clear_import_results', methods=['POST'])
def clear_import_results():
    if 'import_results' in session:
        session.pop('import_results', None)
    return jsonify({'success': True})



