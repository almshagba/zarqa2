import re

def fix_models_file():
    models_file = 'models.py'
    
    try:
        # قراءة الملف
        with open(models_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # إنشاء نسخة احتياطية
        with open(f'{models_file}_backup_before_duplicate_fix', 'w', encoding='utf-8') as f:
            f.write(content)
        
        # حذف الأعمدة المكررة (الثانية من كل نوع)
        lines = content.split('\n')
        cleaned_lines = []
        seen_columns = set()
        
        duplicate_patterns = [
            'can_view_employee_reports = db.Column',
            'can_view_school_reports = db.Column', 
            'can_view_comprehensive_reports = db.Column',
            'can_view_system_logs = db.Column',
            'can_manage_system_settings = db.Column'
        ]
        
        for line in lines:
            line_stripped = line.strip()
            
            # فحص إذا كان السطر يحتوي على عمود مكرر
            is_duplicate = False
            for pattern in duplicate_patterns:
                if pattern in line_stripped:
                    if pattern in seen_columns:
                        # هذا عمود مكرر، تجاهله
                        is_duplicate = True
                        print(f"حذف العمود المكرر: {line_stripped}")
                        break
                    else:
                        # أول مرة نرى هذا العمود
                        seen_columns.add(pattern)
            
            if not is_duplicate:
                cleaned_lines.append(line)
        
        # كتابة الملف المُنظف
        cleaned_content = '\n'.join(cleaned_lines)
        with open(models_file, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        
        print("تم إصلاح ملف models.py بنجاح!")
        print("تم حذف الأعمدة المكررة التالية:")
        for pattern in duplicate_patterns:
            if pattern in seen_columns:
                print(f"- {pattern.split(' = ')[0]}")
        
        return True
        
    except Exception as e:
        print(f"خطأ في إصلاح الملف: {e}")
        return False

if __name__ == "__main__":
    fix_models_file()