#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AWS Deployment Script
Script to help deploy the Flask application to AWS
"""

import boto3
import os
import json
from botocore.exceptions import ClientError

def create_s3_bucket(bucket_name, region='us-east-1'):
    """
    إنشاء S3 bucket لتخزين الملفات
    """
    try:
        s3_client = boto3.client('s3', region_name=region)
        
        if region == 'us-east-1':
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        
        print(f"تم إنشاء S3 bucket: {bucket_name}")
        return True
    except ClientError as e:
        print(f"خطأ في إنشاء S3 bucket: {e}")
        return False

def create_rds_instance():
    """
    إنشاء RDS instance لقاعدة البيانات
    """
    rds_client = boto3.client('rds')
    
    try:
        response = rds_client.create_db_instance(
            DBInstanceIdentifier='employees-db',
            DBInstanceClass='db.t3.micro',
            Engine='postgres',
            MasterUsername='admin',
            MasterUserPassword='your_secure_password_here',
            AllocatedStorage=20,
            VpcSecurityGroupIds=[
                # أضف security group IDs هنا
            ],
            BackupRetentionPeriod=7,
            MultiAZ=False,
            PubliclyAccessible=True,
            StorageType='gp2'
        )
        
        print("تم إنشاء RDS instance بنجاح")
        return response
    except ClientError as e:
        print(f"خطأ في إنشاء RDS instance: {e}")
        return None

def create_elastic_beanstalk_app():
    """
    إنشاء Elastic Beanstalk application
    """
    eb_client = boto3.client('elasticbeanstalk')
    
    try:
        # إنشاء التطبيق
        app_response = eb_client.create_application(
            ApplicationName='employees-management-system',
            Description='نظام إدارة شؤون الموظفين'
        )
        
        # إنشاء البيئة
        env_response = eb_client.create_environment(
            ApplicationName='employees-management-system',
            EnvironmentName='employees-prod',
            SolutionStackName='64bit Amazon Linux 2 v3.4.0 running Python 3.9',
            OptionSettings=[
                {
                    'Namespace': 'aws:autoscaling:launchconfiguration',
                    'OptionName': 'InstanceType',
                    'Value': 't3.micro'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:application:environment',
                    'OptionName': 'FLASK_ENV',
                    'Value': 'production'
                }
            ]
        )
        
        print("تم إنشاء Elastic Beanstalk application بنجاح")
        return app_response, env_response
    except ClientError as e:
        print(f"خطأ في إنشاء Elastic Beanstalk: {e}")
        return None, None

def main():
    """
    الدالة الرئيسية للنشر
    """
    print("بدء عملية النشر على AWS...")
    
    # قراءة متغيرات البيئة
    bucket_name = os.environ.get('S3_BUCKET', 'employees-system-files')
    region = os.environ.get('AWS_REGION', 'us-east-1')
    
    # إنشاء S3 bucket
    print("إنشاء S3 bucket...")
    create_s3_bucket(bucket_name, region)
    
    # إنشاء RDS instance
    print("إنشاء RDS instance...")
    # create_rds_instance()  # قم بإلغاء التعليق عند الحاجة
    
    # إنشاء Elastic Beanstalk
    print("إنشاء Elastic Beanstalk application...")
    # create_elastic_beanstalk_app()  # قم بإلغاء التعليق عند الحاجة
    
    print("تم الانتهاء من إعداد البنية التحتية على AWS")
    print("يرجى تحديث متغيرات البيئة في ملف .env")

if __name__ == '__main__':
    main()