@echo off
chcp 65001 > nul
echo ========================================
echo فحص شامل لنظام إدارة الموظفين
echo ========================================
echo.
echo تحذير: تأكد من إغلاق التطبيق تماماً قبل المتابعة!
echo.
pause
echo.
echo جاري تشغيل الفحص الشامل...
echo.
python comprehensive_system_check.py
echo.
echo تم الانتهاء من الفحص
pause