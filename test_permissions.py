#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت اختبار نظام الصلاحيات
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_permissions():
    """اختبار نظام الصلاحيات"""
    try:
        from app import app
        from models import User, db
        
        with app.app_context():
            print("🧪 اختبار نظام الصلاحيات...")
        
            # البحث عن مستخدم مدير
            admin_user = User.query.filter_by(is_admin=True).first()
            if admin_user:
                print(f"✅ تم العثور على مستخدم مدير: {admin_user.username}")
                
                # اختبار صلاحيات المدير
                perms = admin_user.has_permission()
                print(f"📊 عدد صلاحيات المدير: {len(perms)}")
                
                # اختبار صلاحية واحدة
                test_perm = admin_user.has_permission('can_view_employees')
                print(f"🔍 صلاحية can_view_employees للمدير: {test_perm}")
            else:
                print("❌ لم يتم العثور على مستخدم مدير")
            
            # البحث عن مستخدم عادي
            normal_user = User.query.filter_by(is_admin=False).first()
            if normal_user:
                print(f"✅ تم العثور على مستخدم عادي: {normal_user.username}")
                
                # اختبار صلاحيات المستخدم العادي
                perms = normal_user.has_permission()
                active_perms = [k for k, v in perms.items() if v]
                print(f"📊 عدد الصلاحيات النشطة للمستخدم العادي: {len(active_perms)}")
                print(f"📋 الصلاحيات النشطة: {active_perms[:5]}...")  # أول 5 صلاحيات
            else:
                print("❌ لم يتم العثور على مستخدم عادي")
        
            print("✅ انتهى اختبار نظام الصلاحيات")
    except Exception as e:
        print(f"❌ خطأ في اختبار الصلاحيات: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_permissions()
