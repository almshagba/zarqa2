from app import app
from models import db, Employee, School
from datetime import datetime
import sys

# قائمة الموظفين الجدد
employees_data = [
    {
        'ministry_number': '187892',
        'name': 'غاده صلاح عبدالرحيم الحمدان',
        'civil_id': '9782027503',
        'gender': 'أنثى',  # تصحيح الجنس
        'job_title': 'رئيس قسم/مكلف',
        'qualification': 'دبلوم عالي',
        'specialization': 'اداره مدرسيه',
        'phone_number': '781427026',
        'appointment_date': '2013-09-12',
        'department': 'الشؤون الماليه'
    },
    {
        'ministry_number': '110946',
        'name': 'عبدالسلام علي مفلح ابوجابر',
        'civil_id': '9681033941',
        'gender': 'ذكر',
        'job_title': 'امين صندوق',
        'qualification': 'بكالوريوس',
        'specialization': 'علوم اداريه',
        'phone_number': '797481542',
        'appointment_date': '2000-09-14',
        'department': 'الشؤون الماليه'
    },
    {
        'ministry_number': '140985',
        'name': 'نورالدين سعيد علي شومان',
        'civil_id': '9751041720',
        'gender': 'ذكر',
        'job_title': 'محاسب',
        'qualification': 'بكالوريوس',
        'specialization': 'محاسبه',
        'phone_number': '788703623',
        'appointment_date': '2006-04-17',
        'department': 'الشؤون الماليه'
    },
    {
        'ministry_number': '176953',
        'name': 'فداء احمد شحاده النجار',
        'civil_id': '9822001861',
        'gender': 'أنثى',  # تصحيح الجنس
        'job_title': 'محاسب',
        'qualification': 'بكالوريوس',
        'specialization': 'محاسبه',
        'phone_number': '786709871',
        'appointment_date': '2011-08-29',
        'department': 'الشؤون الماليه'
    },
    {
        'ministry_number': '204605',
        'name': 'محمد ابراهيم حسن النواس',
        'civil_id': '9871048640',
        'gender': 'ذكر',
        'job_title': 'معلم',
        'qualification': 'دبلوم عالي',
        'specialization': 'تربيه',
        'phone_number': '797618225',
        'appointment_date': '2018-10-07',
        'department': 'الشؤون الماليه'
    },
    {
        'ministry_number': '160071',
        'name': 'علي علي محمد قطش',
        'civil_id': '9741043713',
        'gender': 'ذكر',
        'job_title': 'امين عهده',
        'qualification': 'دبلوم متوسط',
        'specialization': 'اداره الاعمال',
        'phone_number': '788805880',
        'appointment_date': '2008-10-05',
        'department': 'اللوازم والكتب المدرسية والنقليات'
    },
    {
        'ministry_number': '185010',
        'name': 'انس محمد عوض الصالح',
        'civil_id': '9861063154',
        'gender': 'ذكر',
        'job_title': 'امين لوازم',
        'qualification': 'بكالوريوس',
        'specialization': 'نظم المعلومات الاداريه',
        'phone_number': '785183607',
        'appointment_date': '2013-08-21',
        'department': 'اللوازم والكتب المدرسية والنقليات'
    },
    {
        'ministry_number': '187259',
        'name': 'لؤي عبدالفتاح مصطفى المعايطه',
        'civil_id': '9871052574',
        'gender': 'ذكر',
        'job_title': 'امين سجل',
        'qualification': 'بكالوريوس',
        'specialization': 'نظم المعلومات الاداريه',
        'phone_number': '781575616',
        'appointment_date': '2013-10-07',
        'department': 'اللوازم والكتب المدرسية والنقليات'
    },
    {
        'ministry_number': '185645',
        'name': 'زيد خليل صالح السروجي',
        'civil_id': '9761017100',
        'gender': 'ذكر',
        'job_title': 'امين مستودع',
        'qualification': 'بكالوريوس',
        'specialization': 'اداره اعمال',
        'phone_number': '799253053',
        'appointment_date': '2013-09-01',
        'department': 'اللوازم والكتب المدرسية والنقليات'
    },
    {
        'ministry_number': '167716',
        'name': 'محمود محمد محمود رباح',
        'civil_id': '9761050835',
        'gender': 'ذكر',
        'job_title': 'امين مستودع',
        'qualification': 'بكالوريوس',
        'specialization': 'محاسبه',
        'phone_number': '786363452',
        'appointment_date': '2009-12-03',
        'department': 'اللوازم والكتب المدرسية والنقليات'
    },
    {
        'ministry_number': '156327',
        'name': 'ابراهيم عزت عبدالله السوالمه',
        'civil_id': '9661017469',
        'gender': 'ذكر',
        'job_title': 'اداري',
        'qualification': 'بكالوريوس',
        'specialization': 'اداره اعمال',
        'phone_number': '786104139',
        'appointment_date': '2008-02-03',
        'department': 'اللوازم والكتب المدرسية والنقليات'
    },
    {
        'ministry_number': '185630',
        'name': 'علي محمد علي حشكي',
        'civil_id': '9861040804',
        'gender': 'ذكر',
        'job_title': 'معلم',
        'qualification': 'بكالوريوس',
        'specialization': 'معلم صف',
        'phone_number': '780340789',
        'appointment_date': '2013-08-19',
        'department': 'اللوازم والكتب المدرسية والنقليات'
    },
    {
        'ministry_number': '163394',
        'name': 'احمد محمود منيب سيد',
        'civil_id': '9801057485',
        'gender': 'ذكر',
        'job_title': 'فني حاسوب مدرسة',
        'qualification': 'دبلوم متوسط',
        'specialization': 'تكنولوجيا المعلومات',
        'phone_number': '799141443',
        'appointment_date': '2009-08-23',
        'department': 'اللوازم والكتب المدرسية والنقليات'
    },
    {
        'ministry_number': '208054',
        'name': 'محمد احمد عناد الذنيبات',
        'civil_id': '9941017689',
        'gender': 'ذكر',
        'job_title': 'معلم',
        'qualification': 'بكالوريوس',
        'specialization': 'المصارف الاسلاميه',
        'phone_number': '777836250',
        'appointment_date': '2019-09-11',
        'department': 'اللوازم والكتب المدرسية والنقليات'
    },
    {
        'ministry_number': '157589',
        'name': 'هشام هاشم صالح برهم',
        'civil_id': '9711036636',
        'gender': 'ذكر',
        'job_title': 'كاتب مدرسه',
        'qualification': 'دبلوم متوسط',
        'specialization': 'اداره الاعمال',
        'phone_number': '799717108',
        'appointment_date': '2008-08-12',
        'department': 'اللوازم والكتب المدرسية والنقليات'
    },
    {
        'ministry_number': '162631',
        'name': 'حسن ابراهيم عبدالحفيظ القطراوي',
        'civil_id': '9811043895',
        'gender': 'ذكر',
        'job_title': 'معلم',
        'qualification': 'دبلوم عالي',
        'specialization': 'نظم المعلومات الاداريه',
        'phone_number': '787144693',
        'appointment_date': '2009-04-02',
        'department': 'اللوازم والكتب المدرسية والنقليات'
    },
    {
        'ministry_number': '105676',
        'name': 'سالم احمد عبدالقادر الزواهره',
        'civil_id': '9761038232',
        'gender': 'ذكر',
        'job_title': 'معلم',
        'qualification': 'دبلوم عالي',
        'specialization': 'اداره مدرسيه',
        'phone_number': '786931598',
        'appointment_date': '1999-11-24',
        'department': 'اللوازم والكتب المدرسية والنقليات'
    },
    {
        'ministry_number': '178414',
        'name': 'حازم حامد مصباح المحيسن',
        'civil_id': '9891052194',
        'gender': 'ذكر',
        'job_title': 'عضو قسم',
        'qualification': 'بكالوريوس',
        'specialization': 'ادارة مياه ومصادر طبيعيه',
        'phone_number': '785382959',
        'appointment_date': '2012-08-23',
        'department': 'النشاطات التربوية'
    },
    {
        'ministry_number': '155692',
        'name': 'رشا نظام درويش بزيني',
        'civil_id': '9822015970',
        'gender': 'أنثى',  # تصحيح الجنس
        'job_title': 'اداري',
        'qualification': 'بكالوريوس',
        'specialization': 'تربيه رياضيه',
        'phone_number': '780014237',
        'appointment_date': '2008-01-02',
        'department': 'النشاطات التربوية'
    },
    {
        'ministry_number': '144728',
        'name': 'محمد عبدالحكيم سلامه اشتيوي',
        'civil_id': '9831045657',
        'gender': 'ذكر',
        'job_title': 'عضو قسم',
        'qualification': 'دبلوم عالي',
        'specialization': 'السياسات العامة وحقوق الطفل',
        'phone_number': '799458968',
        'appointment_date': '2006-08-24',
        'department': 'النشاطات التربوية'
    },
    {
        'ministry_number': '189977',
        'name': 'نهى سليمان علي العليمات',
        'civil_id': '9762002984',
        'gender': 'أنثى',  # تصحيح الجنس
        'job_title': 'عضو قسم',
        'qualification': 'بكالوريوس',
        'specialization': 'معلم صف',
        'phone_number': '772277985',
        'appointment_date': '2014-09-07',
        'department': 'النشاطات التربوية'
    },
    {
        'ministry_number': '98459',
        'name': 'ياسر شحاده خالد السايس',
        'civil_id': '9701002498',
        'gender': 'ذكر',
        'job_title': 'اداري',
        'qualification': 'دبلوم عالي',
        'specialization': 'اداره مدرسيه',
        'phone_number': '786706585',
        'appointment_date': '1996-10-16',
        'department': 'النشاطات التربوية'
    },
    {
        'ministry_number': '104638',
        'name': 'هشام جهاد جابر الجندي',
        'civil_id': '9721038798',
        'gender': 'ذكر',
        'job_title': 'رئيس قسم',
        'qualification': 'دبلوم عالي',
        'specialization': 'اداره مدرسيه',
        'phone_number': '797129294',
        'appointment_date': '1999-09-22',
        'department': 'النشاطات التربوية'
    },
    {
        'ministry_number': '124537',
        'name': 'نضال رباح صبري الخولي',
        'civil_id': '9791038612',
        'gender': 'ذكر',
        'job_title': 'عضو قسم',
        'qualification': 'دبلوم عالي',
        'specialization': 'تكنولوجيا المعلومات والاتصالات',
        'phone_number': '790103111',
        'appointment_date': '2003-09-16',
        'department': 'النشاطات التربوية'
    },
    {
        'ministry_number': '114376',
        'name': 'حنان فهد بخيت العليمات',
        'civil_id': '9782051140',
        'gender': 'أنثى',  # تصحيح الجنس
        'job_title': 'مساعد مدير مدرسه',
        'qualification': 'دبلوم عالي',
        'specialization': 'تكنولوجيا المعلومات والاتصالات',
        'phone_number': '790013691',
        'appointment_date': '2001-08-26',
        'department': 'النشاطات التربوية'
    },
    {
        'ministry_number': '155006',
        'name': 'الاء احمد خليف الزيود',
        'civil_id': '9852045901',
        'gender': 'أنثى',  # تصحيح الجنس
        'job_title': 'اداري',
        'qualification': 'بكالوريوس',
        'specialization': 'علم الحاسوب',
        'phone_number': '779439469',
        'appointment_date': '2007-10-25',
        'department': 'تكنولوجيا التعليم والمعلومات'
    },
    {
        'ministry_number': '140976',
        'name': 'علي محمود مصطفى حامد',
        'civil_id': '9781022968',
        'gender': 'ذكر',
        'job_title': 'فني اجهزه',
        'qualification': 'دبلوم متوسط',
        'specialization': 'هندسه كهربائيه/قوى',
        'phone_number': '786902095',
        'appointment_date': '2006-04-04',
        'department': 'تكنولوجيا التعليم والمعلومات'
    },
    {
        'ministry_number': '140979',
        'name': 'خالد رمضان احمد جعاره',
        'civil_id': '9811058613',
        'gender': 'ذكر',
        'job_title': 'امين مكتبه',
        'qualification': 'بكالوريوس',
        'specialization': 'مكتبات',
        'phone_number': '785246330',
        'appointment_date': '2006-04-13',
        'department': 'تكنولوجيا التعليم والمعلومات'
    },
    {
        'ministry_number': '148443',
        'name': 'محمد خالد ابراهيم الشيخ يوسف',
        'civil_id': '9801002751',
        'gender': 'ذكر',
        'job_title': 'مبرمج مساعد',
        'qualification': 'بكالوريوس',
        'specialization': 'علم الحاسوب',
        'phone_number': '788377410',
        'appointment_date': '2006-10-30',
        'department': 'تكنولوجيا التعليم والمعلومات'
    },
    {
        'ministry_number': '152087',
        'name': 'نبيله محمد عبدالهادي راس',
        'civil_id': '9752019656',
        'gender': 'أنثى',  # تصحيح الجنس
        'job_title': 'مهندس حاسوب',
        'qualification': 'بكالوريوس',
        'specialization': 'هندسة حاسوب',
        'phone_number': '776364194',
        'appointment_date': '2007-08-26',
        'department': 'تكنولوجيا التعليم والمعلومات'
    },
    {
        'ministry_number': '108170',
        'name': 'حسام حسين محمد ابومنشار',
        'civil_id': '9771045444',
        'gender': 'ذكر',
        'job_title': 'رئيس قسم',
        'qualification': 'ماجستير',
        'specialization': 'علم الحاسوب',
        'phone_number': '776774244',
        'appointment_date': '2000-09-05',
        'department': 'تكنولوجيا التعليم والمعلومات'
    },
    {
        'ministry_number': '151188',
        'name': 'رولا سليمان ابراهيم العمرات',
        'civil_id': '9842039035',
        'gender': 'أنثى',  # تصحيح الجنس
        'job_title': 'مهندس حاسوب',
        'qualification': 'ماجستير',
        'specialization': 'الامن السيبراني',
        'phone_number': '776364194',
        'appointment_date': '2007-08-02',
        'department': 'تكنولوجيا التعليم والمعلومات'
    },
    {
        'ministry_number': '121809',
        'name': 'هشام عبدالله صالح ابوزروق',
        'civil_id': '9691015575',
        'gender': 'ذكر',
        'job_title': 'مهندس',
        'qualification': 'بكالوريوس',
        'specialization': 'هندسة حاسوب',
        'phone_number': '798199603',
        'appointment_date': '2002-10-28',
        'department': 'تكنولوجيا التعليم والمعلومات'
    },
    {
        'ministry_number': '138328',
        'name': 'عاطف محمد احمد الزواهرة',
        'civil_id': '9821037883',
        'gender': 'ذكر',
        'job_title': 'رئيس قسم',
        'qualification': 'دكتوراة',
        'specialization': 'مناهج واساليب تدريس',
        'phone_number': '',
        'appointment_date': '',
        'department': 'شؤون الموظفين'
    },
    {
        'ministry_number': '148445',
        'name': 'ماهر محمد ذياب المحاميد',
        'civil_id': '9691002384',
        'gender': 'ذكر',
        'job_title': 'كاتب',
        'qualification': 'بكالوريوس',
        'specialization': 'اداره اعمال',
        'phone_number': '787722505',
        'appointment_date': '2006-10-30',
        'department': 'شؤون الموظفين'
    },
    {
        'ministry_number': '152088',
        'name': 'نجاه يحيى علي ابوجعفر',
        'civil_id': '9752024427',
        'gender': 'أنثى',  # تصحيح الجنس
        'job_title': 'اداري',
        'qualification': 'دبلوم عالي',
        'specialization': 'اداره مدرسيه',
        'phone_number': '795817272',
        'appointment_date': '2007-08-12',
        'department': 'شؤون الموظفين'
    },
    {
        'ministry_number': '158723',
        'name': 'اسامه انور فائق مصلح',
        'civil_id': '9861034200',
        'gender': 'ذكر',
        'job_title': 'اداري',
        'qualification': 'دبلوم عالي',
        'specialization': 'السياسات العامة وحقوق الطفل',
        'phone_number': '788065432',
        'appointment_date': '2008-08-25',
        'department': 'شؤون الموظفين'
    },
    {
        'ministry_number': '176910',
        'name': 'اسماء ياسر محمد النادي',
        'civil_id': '9812016329',
        'gender': 'أنثى',  # تصحيح الجنس
        'job_title': 'اداري',
        'qualification': 'ماجستير',
        'specialization': 'اداره عامه',
        'phone_number': '785781699',
        'appointment_date': '2011-08-28',
        'department': 'شؤون الموظفين'
    },
    {
        'ministry_number': '176926',
        'name': 'سلوى يعقوب طعمه جبرين',
        'civil_id': '9772017389',
        'gender': 'أنثى',  # تصحيح الجنس
        'job_title': 'اداري',
        'qualification': 'بكالوريوس',
        'specialization': 'اداره اعمال',
        'phone_number': '786345278',
        'appointment_date': '2011-09-06',
        'department': 'شؤون الموظفين'
    },
    {
        'ministry_number': '160155',
        'name': 'ايمن سليم نهار شبيطه',
        'civil_id': '9871019336',
        'gender': 'ذكر',
        'job_title': 'كاتب',
        'qualification': 'دبلوم متوسط',
        'specialization': 'اداره الاعمال',
        'phone_number': '785083056',
        'appointment_date': '2008-10-07',
        'department': 'شؤون الموظفين'
    },
    {
        'ministry_number': '138099',
        'name': 'انس عبدالملك عوض ابوليل',
        'civil_id': '9831017417',
        'gender': 'ذكر',
        'job_title': 'معلم',
        'qualification': 'دبلوم عالي',
        'specialization': 'صعوبات التعلم',
        'phone_number': '789174239',
        'appointment_date': '2005-08-30',
        'department': 'شؤون الموظفين'
    },
    {
        'ministry_number': '138320',
        'name': 'عبدالرحمن محمد جمعه محمد زين ابوطوق',
        'civil_id': '9831021919',
        'gender': 'ذكر',
        'job_title': 'معلم',
        'qualification': 'بكالوريوس',
        'specialization': 'معلم صف',
        'phone_number': '78078779',
        'appointment_date': '2005-08-30',
        'department': 'شؤون الموظفين'
    },
    {
        'ministry_number': '161354',
        'name': 'منوى قاسم عبدالله شاهين',
        'civil_id': '9842039303',
        'gender': 'أنثى',
        'job_title': 'مشرف تربوي',
        'qualification': 'دبلوم عالي',
        'specialization': 'ادارة تربوية',
        'phone_number': '787307033',
        'appointment_date': '2008-11-08',
        'department': 'الاشراف التربوي'
    },
    {
        'ministry_number': '103732',
        'name': 'نادية نعيم محمد الاحمد',
        'civil_id': '9782054183',
        'gender': 'أنثى',
        'job_title': 'مشرف تربوي',
        'qualification': 'ماجستير',
        'specialization': 'فيزياء تطبيقية',
        'phone_number': '790322954',
        'appointment_date': '2010-09-04',
        'department': 'الاشراف التربوي'
    },
    {
        'ministry_number': '165311',
        'name': 'خلود علي عبد الرحيم صالح',
        'civil_id': '9852032667',
        'gender': 'أنثى',
        'job_title': 'مشرف تربوي',
        'qualification': 'ماجستير',
        'specialization': 'ادارة تربوية',
        'phone_number': '786113856',
        'appointment_date': '2009-08-16',
        'department': 'الاشراف التربوي'
    },
    {
        'ministry_number': '174838',
        'name': 'براء اسماعيل محمد الغوانمة',
        'civil_id': '9852047662',
        'gender': 'ذكر',
        'job_title': 'مشرف تربوي',
        'qualification': 'دبلوم عالي',
        'specialization': 'إدارة تربوية',
        'phone_number': '777977795',
        'appointment_date': '2011-08-23',
        'department': 'الاشراف التربوي'
    },
    {
        'ministry_number': '144366',
        'name': 'علي عايد سليمان الزيود',
        'civil_id': '9831033946',
        'gender': 'ذكر',
        'job_title': 'مشرف تربوي',
        'qualification': 'دكتوراة',
        'specialization': 'مناهج وأساليب تدريس لغة إنجليزية',
        'phone_number': '777059015',
        'appointment_date': '2006-08-16',
        'department': 'الاشراف التربوي'
    },
    {
        'ministry_number': '100049',
        'name': 'سلطان عيسى سنين الشعار',
        'civil_id': '9751019279',
        'gender': 'ذكر',
        'job_title': 'مشرف تربوي',
        'qualification': 'دكتوراة',
        'specialization': 'اللغة العربية',
        'phone_number': '796598829',
        'appointment_date': '1997-02-24',
        'department': 'الاشراف التربوي'
    },
    {
        'ministry_number': '136818',
        'name': 'هدى عبد الرحمن صالح الزعبي',
        'civil_id': '9832028422',
        'gender': 'أنثى',
        'job_title': 'مشرف تربوي',
        'qualification': 'ماجستير',
        'specialization': 'اساليب تدريس العلوم',
        'phone_number': '797378975',
        'appointment_date': '2005-08-31',
        'department': 'الاشراف التربوي'
    },
    {
        'ministry_number': '145990',
        'name': 'لمى كامل عبد الامير الربيعي',
        'civil_id': '2000590050',
        'gender': 'أنثى',
        'job_title': 'مشرف تربوي',
        'qualification': 'ماجستير',
        'specialization': 'تربية فنية',
        'phone_number': '795373585',
        'appointment_date': '2006-08-30',
        'department': 'الاشراف التربوي'
    },
    {
        'ministry_number': '151974',
        'name': 'مراد ربحي جودت المصري',
        'civil_id': '9851013013',
        'gender': 'ذكر',
        'job_title': 'مشرف تربوي',
        'qualification': 'دبلوم عالي',
        'specialization': 'دبلوم عالي في التربية',
        'phone_number': '788889974',
        'appointment_date': '2007-08-12',
        'department': 'الاشراف التربوي'
    },
    {
        'ministry_number': '138404',
        'name': 'ايمان خالد عيسى علي',
        'civil_id': '9802037469',
        'gender': 'أنثى',
        'job_title': 'مشرف تربوي',
        'qualification': 'ماجستير',
        'specialization': 'مناهج واساليب تدريس',
        'phone_number': '780344973',
        'appointment_date': '2005-08-14',
        'department': 'الاشراف التربوي'
    },
    {
        'ministry_number': '105943',
        'name': 'ختام محمد علي العليمات',
        'civil_id': '9772003261',
        'gender': 'أنثى',
        'job_title': 'مشرف تربوي',
        'qualification': 'دبلوم عالي',
        'specialization': 'ادارة مدرسية',
        'phone_number': '772687466',
        'appointment_date': '2024-11-15',
        'department': 'الاشراف التربوي'
    },
    {
        'ministry_number': '110927',
        'name': 'خليل علي عبد القادر دردس',
        'civil_id': '9771023167',
        'gender': 'ذكر',
        'job_title': 'مشرف تربوي',
        'qualification': 'ماجستير',
        'specialization': 'الإدارة والدراسات الإستراتيجية',
        'phone_number': '781371867',
        'appointment_date': '2000-09-28',
        'department': 'الاشراف التربوي'
    },
    {
        'ministry_number': '125754',
        'name': 'شاهر مد الله عواد العثمان',
        'civil_id': '9801039819',
        'gender': 'ذكر',
        'job_title': 'مشرف تربوي',
        'qualification': 'ماجستير',
        'specialization': 'اللغة الإنجليزية وآدابها-اللغويات',
        'phone_number': '788452559',
        'appointment_date': '2003-08-28',
        'department': 'الاشراف التربوي'
    },
    {
        'ministry_number': '174952',
        'name': 'أيمن سلامة محمد صعلوك',
        'civil_id': '9881018519',
        'gender': 'ذكر',
        'job_title': 'مشرف تربوي',
        'qualification': 'دكتوراة',
        'specialization': 'دراسات لغوية+ دبلوم عالي في التربية',
        'phone_number': '789812266',
        'appointment_date': '2011-09-11',
        'department': 'الاشراف التربوي'
    },
    {
        'ministry_number': '119518',
        'name': 'ريم رفيق عبدالكريم موافي',
        'civil_id': '9802025949',
        'gender': 'أنثى',
        'job_title': 'مشرف تربوي',
        'qualification': 'ماجستير',
        'specialization': 'علم الحاسوب',
        'phone_number': '777664224',
        'appointment_date': '2002-08-27',
        'department': 'الاشراف التربوي'
    },
    {
        'ministry_number': '122705',
        'name': 'رانية بشير حسن عمر',
        'civil_id': '9802047575',
        'gender': 'أنثى',
        'job_title': 'مشرف تربوي',
        'qualification': 'ماجستير',
        'specialization': 'اللغة الانجليزية و آدابها',
        'phone_number': '796804304',
        'appointment_date': '2003-09-01',
        'department': 'الاشراف التربوي'
    },
    {
        'ministry_number': '146001',
        'name': 'ايمان احمد محمد فريحات',
        'civil_id': '9792016352',
        'gender': 'أنثى',
        'job_title': 'مشرف تربوي',
        'qualification': 'دكتوراة',
        'specialization': 'مناهج وأساليب تدريس',
        'phone_number': '788819569',
        'appointment_date': '2006-08-16',
        'department': 'الاشراف التربوي'
    },
    {
        'ministry_number': '152175',
        'name': 'ريما محمود عليوي الزيودي',
        'civil_id': '9812035942',
        'gender': 'أنثى',
        'job_title': 'مشرف تربوي',
        'qualification': 'دكتوراة',
        'specialization': 'تاريخ',
        'phone_number': '772569842',
        'appointment_date': '2007-08-12',
        'department': 'الاشراف التربوي'
    },
    {
        'ministry_number': '151844',
        'name': 'نبيـــل عايد كساب شديفــــات',
        'civil_id': '9811037942',
        'gender': 'ذكر',
        'job_title': 'مشرف تربوي',
        'qualification': 'ماجستير',
        'specialization': 'الادارة التربوية',
        'phone_number': '797573790',
        'appointment_date': '2007-08-12',
        'department': 'الاشراف التربوي'
    },
    {
        'ministry_number': '159392',
        'name': 'عمر محمود علي مومني',
        'civil_id': '9841013898',
        'gender': 'ذكر',
        'job_title': 'مشرف تربوي',
        'qualification': 'ماجستير',
        'specialization': 'إشراف تربوي',
        'phone_number': '782324585',
        'appointment_date': '2008-08-03',
        'department': 'الاشراف التربوي'
    },
    {
        'ministry_number': '132260',
        'name': 'علي توفيق حمدان مشاقبه',
        'civil_id': '9821012076',
        'gender': 'ذكر',
        'job_title': 'مشرف تربوي',
        'qualification': 'ماجستير',
        'specialization': 'مناهج التربية المهنية وأساليب تدريسها',
        'phone_number': '772687511',
        'appointment_date': '2005-08-14',
        'department': 'الاشراف التربوي'
    },
    {
        'ministry_number': '144827',
        'name': 'نريمان راتب محمد عريقات',
        'civil_id': '9722039345',
        'gender': 'أنثى',
        'job_title': 'مشرف تربوي',
        'qualification': 'دبلوم عالي',
        'specialization': 'احياء تطبيقيه',
        'phone_number': '772499239',
        'appointment_date': '2006-09-14',
        'department': 'الاشراف التربوي'
    },
    {
        'ministry_number': '173408',
        'name': 'اماني يوسف عبد اللطيف الحميد',
        'civil_id': '9822035537',
        'gender': 'أنثى',
        'job_title': 'مشرف تربوي',
        'qualification': 'دكتوراة',
        'specialization': 'التربية الرياضية',
        'phone_number': '782959021',
        'appointment_date': '2011-03-06',
        'department': 'الاشراف التربوي'
    },
    {
        'ministry_number': '109817',
        'name': 'أمجد عايش عبد الهادي ابو لحية',
        'civil_id': '9721047119',
        'gender': 'ذكر',
        'job_title': 'مشرف تربوي',
        'qualification': 'ماجستير',
        'specialization': 'التربيه في الاسلام',
        'phone_number': '790958595',
        'appointment_date': '2000-09-10',
        'department': 'الاشراف التربوي'
    },
    {
        'ministry_number': '119506',
        'name': 'فاتن مشرف محمد عامر',
        'civil_id': '9792046381',
        'gender': 'أنثى',
        'job_title': 'مشرف تربوي',
        'qualification': 'ماجستير',
        'specialization': 'تربية خاصة',
        'phone_number': '781424770',
        'appointment_date': '2002-08-26',
        'department': 'الاشراف التربوي'
    },
    {
        'ministry_number': '187939',
        'name': 'ابتسام أحمد عبد الرحاحلة',
        'civil_id': '9752021425',
        'gender': 'أنثى',
        'job_title': 'مشرف تربوي',
        'qualification': 'دبلوم عالي',
        'specialization': 'إدارة تربوية',
        'phone_number': '772714804',
        'appointment_date': '2013-07-22',
        'department': 'الاشراف التربوي'
    },
    {
        'ministry_number': '176919',
        'name': 'الهام خالد فاضل الزيود',
        'civil_id': '9842041475',
        'gender': 'أنثى',
        'job_title': 'مشرف تربوي',
        'qualification': 'ماجستير',
        'specialization': 'بكا معلم صف / ماجستير مناهج واساليب تدريس',
        'phone_number': '776052310',
        'appointment_date': '2011-08-29',
        'department': 'الاشراف التربوي'
    }
]

def add_directorate_employees():
    with app.app_context():
        added_count = 0
        error_count = 0
        skipped_count = 0
        
        print("بدء إضافة موظفي المديرية...")
        
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
                school = School.query.filter_by(name=emp_data['department']).first()
                if not school:
                    school = School(
                        name=emp_data['department'],
                        region='المديرية',
                        type='قسم إداري',
                        gender='مختلط'
                    )
                    db.session.add(school)
                    db.session.commit()
                    print(f"تم إنشاء قسم جديد: {emp_data['department']}")
                
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
                    elif emp_data['qualification'] == 'دكتوراة':
                        specialization_field['phd_specialization'] = emp_data['specialization']
                    else:
                        specialization_field['bachelor_specialization'] = emp_data['specialization']
                
                # إنشاء الموظف الجديد
                new_employee = Employee(
                    ministry_number=emp_data['ministry_number'],
                    name=emp_data['name'],
                    civil_id=emp_data['civil_id'],
                    gender=emp_data['gender'],
                    job_title=emp_data['job_title'],
                    qualification=emp_data['qualification'],
                    phone_number=emp_data.get('phone_number', ''),
                    appointment_date=appointment_date,
                    school_id=school.id,
                    is_directorate_employee=True,
                    **specialization_field
                )
                
                db.session.add(new_employee)
                db.session.commit()
                
                print(f"تم إضافة الموظف: {emp_data['name']} - القسم: {emp_data['department']}")
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
            dept = emp['department']
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
        
        print("\nتم الانتهاء من إضافة موظفي المديرية.")

if __name__ == '__main__':
    add_directorate_employees()