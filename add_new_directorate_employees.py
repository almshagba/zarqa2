from app import app
from models import db, Employee, School
from datetime import datetime
import sys

# قائمة الموظفين الجدد المطلوب إضافتهم
employees_data = [
    {
        'ministry_number': '149981',
        'name': 'ابراهيم حمود رزق العموش',
        'civil_id': '9841016785',
        'gender': 'ذكر',
        'job_title': 'الوظيفة',
        'qualification': 'بكالوريوس',
        'specialization': 'لغه انجليزيه',
        'phone_number': '',
        'appointment_date': '2007-03-29',
        'department': 'التدقيق المالي'
    },
    {
        'ministry_number': '140981',
        'name': 'محمد زياد نجيب عبدالنور',
        'civil_id': '9771032265',
        'gender': 'ذكر',
        'job_title': 'محاسب مساعد',
        'qualification': 'دبلوم عالي',
        'specialization': 'القيادة المدرسية',
        'phone_number': '',
        'appointment_date': '2006-04-05',
        'department': 'التدقيق المالي'
    },
    {
        'ministry_number': '121171',
        'name': 'باسمه صالح صبيح النعيمات',
        'civil_id': '9742046764',
        'gender': 'أنثى',
        'job_title': 'رئيس قسم',
        'qualification': 'دبلوم',
        'specialization': 'تربيه الطفل',
        'phone_number': '',
        'appointment_date': '2002-08-25',
        'department': 'الديوان'
    },
    {
        'ministry_number': '186715',
        'name': 'مخلص توحيد محمود الشيدى',
        'civil_id': '9711024772',
        'gender': 'ذكر',
        'job_title': 'عضو قسم',
        'qualification': 'بكالوريوس',
        'specialization': 'علم الحاسوب',
        'phone_number': '',
        'appointment_date': '2013-10-30',
        'department': 'الديوان'
    },
    {
        'ministry_number': '98861',
        'name': 'محمد عبدالسلام حسن شموط',
        'civil_id': '9701040304',
        'gender': 'ذكر',
        'job_title': 'عضو قسم',
        'qualification': 'ماجستير',
        'specialization': 'مناهج واساليب',
        'phone_number': '',
        'appointment_date': '1996-09-14',
        'department': 'الديوان'
    },
    {
        'ministry_number': '178482',
        'name': 'سناء جمال حسن سمور',
        'civil_id': '9722048628',
        'gender': 'أنثى',
        'job_title': 'رئيس قسم',
        'qualification': 'دبلوم',
        'specialization': 'لغه عربيه',
        'phone_number': '',
        'appointment_date': '2012-08-26',
        'department': 'الديوان'
    },
    {
        'ministry_number': '162638',
        'name': 'محمود مفلح عبدالله العموش',
        'civil_id': '9791022894',
        'gender': 'ذكر',
        'job_title': 'عضو قسم',
        'qualification': 'بكالوريوس',
        'specialization': '',
        'phone_number': '',
        'appointment_date': '2009-03-29',
        'department': 'الديوان'
    },
    {
        'ministry_number': '156755',
        'name': 'عبد البارى احمد عوده الزواهره',
        'civil_id': '9791040488',
        'gender': 'ذكر',
        'job_title': 'عضو قسم',
        'qualification': 'دبلوم عالي',
        'specialization': 'تكنولوجيا المعلومات والاتصالات',
        'phone_number': '',
        'appointment_date': '2000-04-25',
        'department': 'اللوازم والكتب المدرسية والنقليات'
    },
    {
        'ministry_number': '156326',
        'name': 'فادي محمد صالح جعيتم',
        'civil_id': '9741017267',
        'gender': 'ذكر',
        'job_title': 'رئيس قسم',
        'qualification': 'بكالوريوس',
        'specialization': 'محاسبه',
        'phone_number': '',
        'appointment_date': '2008-02-03',
        'department': 'التدقيق المالي'
    },
    {
        'ministry_number': '129462',
        'name': 'محمد سليمان عوده البلوي',
        'civil_id': '9731038268',
        'gender': 'ذكر',
        'job_title': 'محاسب',
        'qualification': 'دبلوم عالي',
        'specialization': 'اداره مدرسيه',
        'phone_number': '',
        'appointment_date': '2004-08-22',
        'department': 'التعليم العام وشؤون الطلبة'
    },
    {
        'ministry_number': '148442',
        'name': 'نبيل محمد علي حامد الحامد',
        'civil_id': '9731026054',
        'gender': 'ذكر',
        'job_title': 'رئيس قسم',
        'qualification': 'بكالوريوس',
        'specialization': 'اداره اعمال',
        'phone_number': '',
        'appointment_date': '2006-10-30',
        'department': 'التعليم العام وشؤون الطلبة'
    },
    {
        'ministry_number': '152486',
        'name': 'محمود جابر محمود الزواهره',
        'civil_id': '9831040533',
        'gender': 'ذكر',
        'job_title': 'كاتب',
        'qualification': 'دكتوراه',
        'specialization': 'دراسات ادبيه ولغويه',
        'phone_number': '',
        'appointment_date': '2002-11-24',
        'department': 'التعليم الخاص'
    },
    {
        'ministry_number': '156325',
        'name': 'ابراهيم بدوي اسماعيل بيدس',
        'civil_id': '9701011934',
        'gender': 'ذكر',
        'job_title': 'اداري',
        'qualification': 'معهد سنتين',
        'specialization': 'اداره الاعمال',
        'phone_number': '',
        'appointment_date': '2008-02-03',
        'department': 'التعليم العام وشؤون الطلبة'
    },
    {
        'ministry_number': '151955',
        'name': 'محمود خلف محمود المشاقبه',
        'civil_id': '9801054236',
        'gender': 'ذكر',
        'job_title': 'محاسب',
        'qualification': 'دكتوراه',
        'specialization': 'مناهج اللغه العربيه واساليب تدريسها',
        'phone_number': '',
        'appointment_date': '2007-08-12',
        'department': 'التعليم العام وشؤون الطلبة'
    },
    {
        'ministry_number': '167878',
        'name': 'سراج حسونه احسان الحشحوش',
        'civil_id': '9661042976',
        'gender': 'ذكر',
        'job_title': 'اداري',
        'qualification': 'معهد سنتين',
        'specialization': 'علوم مصرفيه وماليه',
        'phone_number': '',
        'appointment_date': '2009-12-29',
        'department': 'التعليم العام وشؤون الطلبة'
    },
    {
        'ministry_number': '116452',
        'name': 'باسم كساب فلاح الزيود',
        'civil_id': '9771040098',
        'gender': 'ذكر',
        'job_title': 'عضو قسم',
        'qualification': 'ماجستير',
        'specialization': 'اساليب تدريس اللغه الانجليزيه',
        'phone_number': '',
        'appointment_date': '2001-09-20',
        'department': 'التعليم العام وشؤون الطلبة'
    },
    {
        'ministry_number': '199296',
        'name': 'ختام زعل محمد المعايطة',
        'civil_id': '9812043852',
        'gender': 'أنثى',
        'job_title': 'عضو قسم',
        'qualification': 'ماجستير',
        'specialization': 'ادارة تربوية',
        'phone_number': '',
        'appointment_date': '2016-11-08',
        'department': ''
    },
    {
        'ministry_number': '156324',
        'name': 'ثائر عبدالفتاح ابراهيم الجبر',
        'civil_id': '9831017470',
        'gender': 'ذكر',
        'job_title': 'عضو قسم',
        'qualification': 'بكالوريوس',
        'specialization': 'تمريض',
        'phone_number': '',
        'appointment_date': '2008-02-03',
        'department': 'التعليم العام وشؤون الطلبة'
    },
    {
        'ministry_number': '148441',
        'name': 'ايمن حسن حسين الجدايه',
        'civil_id': '9811023753',
        'gender': 'ذكر',
        'job_title': 'عضو قسم',
        'qualification': 'دبلوم عالي',
        'specialization': 'الادارة والقيادة المدرسية',
        'phone_number': '',
        'appointment_date': '2006-10-30',
        'department': 'التعليم المهني والانتاج'
    },
    {
        'ministry_number': '178484',
        'name': 'شيرين عبدالحميد ابراهيم ابراهيم',
        'civil_id': '9802052019',
        'gender': 'أنثى',
        'job_title': 'عضو قسم',
        'qualification': 'بكالوريوس',
        'specialization': 'محاسبه',
        'phone_number': '',
        'appointment_date': '2012-09-02',
        'department': 'التعليم المهني والانتاج'
    },
    {
        'ministry_number': '209476',
        'name': 'محمد علي محمد الزيود',
        'civil_id': '9921056133',
        'gender': 'ذكر',
        'job_title': 'عضو قسم',
        'qualification': 'دبلوم عالي',
        'specialization': 'تربيه',
        'phone_number': '',
        'appointment_date': '2019-11-04',
        'department': 'التعليم المهني والانتاج'
    },
    {
        'ministry_number': '169917',
        'name': 'محمد زكريا حمد القرعان',
        'civil_id': '9871049731',
        'gender': 'ذكر',
        'job_title': 'عضو قسم',
        'qualification': 'ماجستير',
        'specialization': 'علم الحاسوب',
        'phone_number': '',
        'appointment_date': '2010-09-26',
        'department': 'التعليم المهني والانتاج'
    },
    {
        'ministry_number': '219864',
        'name': 'صفاء عبدالفتاح احمد محمود',
        'civil_id': '9812026213',
        'gender': 'أنثى',
        'job_title': '',
        'qualification': 'بكالوريوس',
        'specialization': 'محاسبه',
        'phone_number': '',
        'appointment_date': '2023-04-26',
        'department': 'الرقابة الداخلية'
    },
    {
        'ministry_number': '145663',
        'name': 'سليمان عبدالرحمن سليمان الزيود',
        'civil_id': '9821029134',
        'gender': 'ذكر',
        'job_title': 'محاسب مساعد',
        'qualification': 'ماجستير',
        'specialization': 'ادارة اعمال',
        'phone_number': '',
        'appointment_date': '2006-09-25',
        'department': 'الرقابة الداخلية'
    },
    {
        'ministry_number': '162413',
        'name': 'فؤاد احمد محمد ابداح',
        'civil_id': '9821060903',
        'gender': 'ذكر',
        'job_title': 'رئيس قسم',
        'qualification': 'بكالوريوس',
        'specialization': 'محاسبه',
        'phone_number': '',
        'appointment_date': '2009-02-28',
        'department': 'الرقابة الداخلية'
    },
    {
        'ministry_number': '172600',
        'name': 'هاني نهار صباح الدهيثم',
        'civil_id': '9881032838',
        'gender': 'ذكر',
        'job_title': 'مدقق داخلي',
        'qualification': 'بكالوريوس',
        'specialization': 'محاسبه',
        'phone_number': '',
        'appointment_date': '2010-12-06',
        'department': 'الرقابة الداخلية'
    },
    {
        'ministry_number': '151844',
        'name': 'نبيـــل عايد كساب شديفــــات',
        'civil_id': '9811037942',
        'gender': 'ذكر',
        'job_title': 'مدقق داخلي',
        'qualification': 'ماجستير',
        'specialization': 'الادارة التربوية',
        'phone_number': '',
        'appointment_date': '2007-08-12',
        'department': 'الاشراف التربوي'
    }
]

def add_directorate_employees():
    """إضافة موظفي المديرية الجدد"""
    with app.app_context():
        added_count = 0
        error_count = 0
        skipped_count = 0
        
        print("بدء إضافة موظفي المديرية الجدد...")
        
        for emp_data in employees_data:
            try:
                # فحص وجود الموظف بالرقم الوزاري أو الرقم المدني
                existing_employee = Employee.query.filter(
                    (Employee.ministry_number == emp_data['ministry_number']) |
                    (Employee.civil_id == emp_data['civil_id'])
                ).first()
                
                if existing_employee:
                    print(f"تم تخطي الموظف {emp_data['name']} - موجود مسبقاً")
                    skipped_count += 1
                    continue
                
                # البحث عن أو إنشاء القسم (المدرسة)
                department_name = emp_data['department'] if emp_data['department'] else 'قسم غير محدد'
                school = School.query.filter_by(name=department_name).first()
                if not school:
                    school = School(
                        name=department_name,
                        region='المديرية',
                        type='قسم إداري',
                        gender='مختلط'
                    )
                    db.session.add(school)
                    db.session.commit()
                    print(f"تم إنشاء قسم جديد: {department_name}")
                
                # تحويل تاريخ التعيين
                if emp_data['appointment_date']:
                    appointment_date = datetime.strptime(emp_data['appointment_date'], '%Y-%m-%d').date()
                else:
                    appointment_date = datetime.now().date()
                
                # تحديد حقل التخصص المناسب بناءً على المؤهل
                specialization_field = {}
                if emp_data['specialization']:
                    if emp_data['qualification'] == 'بكالوريوس':
                        specialization_field['bachelor_specialization'] = emp_data['specialization']
                    elif emp_data['qualification'] == 'دبلوم عالي':
                        specialization_field['high_diploma_specialization'] = emp_data['specialization']
                    elif emp_data['qualification'] == 'ماجستير':
                        specialization_field['masters_specialization'] = emp_data['specialization']
                    elif emp_data['qualification'] == 'دكتوراه':
                        specialization_field['phd_specialization'] = emp_data['specialization']
                    elif emp_data['qualification'] == 'دبلوم':
                        specialization_field['high_diploma_specialization'] = emp_data['specialization']
                    elif emp_data['qualification'] == 'معهد سنتين':
                        specialization_field['bachelor_specialization'] = emp_data['specialization']
                    else:
                        specialization_field['bachelor_specialization'] = emp_data['specialization']
                
                # إنشاء الموظف الجديد
                new_employee = Employee(
                    ministry_number=emp_data['ministry_number'],
                    name=emp_data['name'],
                    civil_id=emp_data['civil_id'],
                    gender=emp_data['gender'],
                    job_title=emp_data['job_title'] if emp_data['job_title'] else 'موظف',
                    qualification=emp_data['qualification'],
                    phone_number=emp_data.get('phone_number', ''),
                    appointment_date=appointment_date,
                    school_id=school.id,
                    is_directorate_employee=True,
                    **specialization_field
                )
                
                db.session.add(new_employee)
                db.session.commit()
                
                print(f"تم إضافة الموظف: {emp_data['name']} - القسم: {department_name}")
                added_count += 1
                
            except Exception as e:
                print(f"خطأ في إضافة الموظف {emp_data['name']}: {str(e)}")
                db.session.rollback()
                error_count += 1
        
        print("\n=== تقرير الإضافة ====")
        print(f"تم إضافة: {added_count} موظف")
        print(f"تم تخطي: {skipped_count} موظف (موجود مسبقاً)")
        print(f"أخطاء: {error_count} موظف")
        print(f"إجمالي الموظفين المعالجين: {len(employees_data)}")
        
        # إحصائيات الأقسام
        departments = {}
        for emp in employees_data:
            dept = emp['department'] if emp['department'] else 'قسم غير محدد'
            if dept not in departments:
                departments[dept] = 0
            departments[dept] += 1
        
        print("\n=== توزيع الموظفين حسب الأقسام ====")
        for dept, count in departments.items():
            print(f"{dept}: {count} موظف")
        
        # إحصائيات الجنس
        gender_stats = {'ذكر': 0, 'أنثى': 0}
        for emp in employees_data:
            gender_stats[emp['gender']] += 1
        
        print("\n=== إحصائيات الجنس ====")
        print(f"ذكور: {gender_stats['ذكر']}")
        print(f"إناث: {gender_stats['أنثى']}")
        
        print("\nتم الانتهاء من إضافة موظفي المديرية الجدد.")

if __name__ == '__main__':
    add_directorate_employees()