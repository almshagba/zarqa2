@echo off
chcp 65001 > nul
echo ========================================
echo إصلاح دالة has_permission
echo ========================================
echo.
echo تحذير: تأكد من إغلاق التطبيق تماماً قبل المتابعة!
echo.
pause
echo.
echo جاري إصلاح دالة has_permission...
echo.
python fix_has_permission_function.py
echo.
echo تم الانتهاء من الإصلاح
pause