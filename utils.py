from flask import request, session
from models import UserLog, db
from datetime import datetime, timedelta

def log_user_activity(user_id, action, module, description=None, target_id=None, target_type=None, status='success', error_message=None):
    """
    دالة لتسجيل أنشطة المستخدمين في النظام
    
    Args:
        user_id: معرف المستخدم
        action: نوع العملية (مثل: تسجيل دخول، إضافة موظف، تعديل، حذف)
        module: الوحدة (مثل: الموظفين، المدارس، الإجازات)
        description: وصف تفصيلي للعملية
        target_id: معرف العنصر المستهدف (إن وجد)
        target_type: نوع العنصر المستهدف (موظف، مدرسة، إلخ)
        status: حالة العملية (success أو failed)
        error_message: رسالة الخطأ في حالة الفشل
    """
    try:
        # الحصول على عنوان IP
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
        
        # الحصول على معلومات المتصفح
        user_agent = request.headers.get('User-Agent')
        
        # إنشاء سجل جديد
        log_entry = UserLog(
            user_id=user_id,
            action=action,
            module=module,
            description=description,
            target_id=target_id,
            target_type=target_type,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
            error_message=error_message
        )
        
        db.session.add(log_entry)
        db.session.commit()
        
    except Exception as e:
        # في حالة فشل تسجيل السجل، لا نريد أن يؤثر على العملية الأساسية
        print(f"خطأ في تسجيل نشاط المستخدم: {str(e)}")
        db.session.rollback()

def get_user_logs(user_id=None, limit=100, offset=0):
    """
    دالة لاسترجاع سجلات المستخدمين
    
    Args:
        user_id: معرف المستخدم (اختياري - إذا لم يتم تحديده سيتم جلب جميع السجلات)
        limit: عدد السجلات المطلوب جلبها
        offset: نقطة البداية
    
    Returns:
        قائمة بسجلات المستخدمين
    """
    query = UserLog.query
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    return query.order_by(UserLog.created_at.desc()).offset(offset).limit(limit).all()

def get_logs_count(user_id=None):
    """
    دالة لحساب عدد السجلات
    
    Args:
        user_id: معرف المستخدم (اختياري)
    
    Returns:
        عدد السجلات
    """
    query = UserLog.query
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    return query.count()

def get_logs_by_module(module, limit=50):
    """
    دالة لاسترجاع السجلات حسب الوحدة
    
    Args:
        module: اسم الوحدة
        limit: عدد السجلات المطلوب جلبها
    
    Returns:
        قائمة بسجلات الوحدة المحددة
    """
    return UserLog.query.filter_by(module=module).order_by(UserLog.created_at.desc()).limit(limit).all()

def get_failed_logs(limit=50):
    """
    دالة لاسترجاع السجلات الفاشلة
    
    Args:
        limit: عدد السجلات المطلوب جلبها
    
    Returns:
        قائمة بالسجلات الفاشلة
    """
    return UserLog.query.filter_by(status='failed').order_by(UserLog.created_at.desc()).limit(limit).all()

def calculate_days_between(start_date, end_date):
    """
    حساب عدد الأيام بين تاريخين (بدون تضمين يوم النهاية)
    
    Args:
        start_date: تاريخ البداية (كائن date)
        end_date: تاريخ النهاية (كائن date)
    
    Returns:
        عدد الأيام بين التاريخين
    """
    delta = end_date - start_date
    return delta.days