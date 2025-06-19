@echo off
chcp 65001 > nul
echo استعادة صلاحيات المدير...
echo.
python fix_admin_permissions.py
echo.
echo تم الانتهاء!
pause