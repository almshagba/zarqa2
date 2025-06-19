@echo off
cd /d "c:\Users\almshagba\Desktop\wael _pro"

REM إنشاء مجلد النسخ الاحتياطية
if not exist "backups" mkdir "backups"

REM إنشاء اسم الملف مع التاريخ
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "datestamp=%YYYY%-%MM%-%DD%_%HH%-%Min%-%Sec%"

REM نسخ قاعدة البيانات
copy "instance\employees.db" "backups\employees_backup_%datestamp%.db"

echo تم إنشاء النسخة الاحتياطية بنجاح: employees_backup_%datestamp%.db
pause