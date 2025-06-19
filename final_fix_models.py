import shutil
import re
from datetime import datetime

def fix_models_file():
    # عمل نسخة احتياطية
    backup_name = f"models_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    shutil.copy('models.py', backup_name)
    print(f"تم إنشاء نسخة احتياطية: {backup_name}")
    
    # قراءة الملف
    with open('models.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # إزالة الأعمدة المكررة والخاطئة (من السطر 384 إلى نهاية نموذج School)
    # البحث عن نهاية نموذج School وإزالة الأعمدة التي تأتي بعدها
    pattern = r'(class School\(db\.Model\):.*?def __repr__\(self\):.*?return f\'<School \{self\.name\}>\'\s*)(\s*can_delete_school.*?)(?=class|$)'
    
    def replace_func(match):
        school_class = match.group(1)
        return school_class + '\n\n'
    
    content = re.sub(pattern, replace_func, content, flags=re.DOTALL)
    
    # إضافة الأعمدة المفقودة داخل نموذج User
    user_pattern = r'(# System permissions\s*can_process_monthly_departures = db\.Column\(db\.Boolean, default=False\)\s*can_view_statistics = db\.Column\(db\.Boolean, default=False\))'
    
    additional_columns = '''
    
    # Report permissions - الأعمدة المفقودة
    can_view_employee_reports = db.Column(db.Boolean, default=False)
    can_view_school_reports = db.Column(db.Boolean, default=False)
    can_view_comprehensive_reports = db.Column(db.Boolean, default=False)
    
    # System permissions - الأعمدة المفقودة
    can_view_system_logs = db.Column(db.Boolean, default=False)
    can_manage_system_settings = db.Column(db.Boolean, default=False)'''
    
    content = re.sub(user_pattern, r'\1' + additional_columns, content)
    
    # كتابة الملف المُحدث
    with open('models.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("تم إصلاح ملف models.py بنجاح!")

if __name__ == '__main__':
    fix_models_file()