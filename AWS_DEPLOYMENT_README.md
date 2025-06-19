# دليل نشر نظام إدارة شؤون الموظفين على AWS

## المتطلبات الأساسية

### 1. حساب AWS
- إنشاء حساب AWS إذا لم يكن لديك واحد
- الحصول على AWS Access Key و Secret Key
- تثبيت AWS CLI

### 2. الأدوات المطلوبة
```bash
# تثبيت AWS CLI
pip install awscli

# تثبيت Docker
# قم بتحميل وتثبيت Docker Desktop

# تثبيت EB CLI (اختياري)
pip install awsebcli
```

## خطوات النشر

### الخطوة 1: إعداد متغيرات البيئة

1. انسخ ملف `.env.example` إلى `.env`:
```bash
cp .env.example .env
```

2. قم بتحديث الملف `.env` بالقيم الصحيحة:
```env
FLASK_ENV=production
SECRET_KEY=your_very_secure_secret_key_here
PORT=5000

# إعدادات قاعدة البيانات (PostgreSQL على RDS)
DATABASE_URL=postgresql://username:password@your-rds-endpoint:5432/employees_db

# إعدادات AWS
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
S3_BUCKET=your-unique-bucket-name
```

### الخطوة 2: إعداد AWS CLI

```bash
aws configure
# أدخل AWS Access Key ID
# أدخل AWS Secret Access Key
# أدخل المنطقة الافتراضية (مثل us-east-1)
# أدخل تنسيق الإخراج الافتراضي (json)
```

### الخطوة 3: إنشاء البنية التحتية على AWS

#### أ. إنشاء S3 Bucket
```bash
# إنشاء bucket لتخزين الملفات
aws s3 mb s3://your-unique-bucket-name --region us-east-1
```

#### ب. إنشاء RDS Instance (PostgreSQL)
```bash
# إنشاء security group لقاعدة البيانات
aws ec2 create-security-group \
    --group-name employees-db-sg \
    --description "Security group for employees database"

# السماح بالاتصال على منفذ PostgreSQL
aws ec2 authorize-security-group-ingress \
    --group-name employees-db-sg \
    --protocol tcp \
    --port 5432 \
    --cidr 0.0.0.0/0

# إنشاء RDS instance
aws rds create-db-instance \
    --db-instance-identifier employees-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --master-username admin \
    --master-user-password YourSecurePassword123 \
    --allocated-storage 20 \
    --vpc-security-group-ids sg-xxxxxxxxx
```

### الخطوة 4: النشر باستخدام Docker و ECR

#### أ. إنشاء ECR Repository
```bash
# إنشاء repository في ECR
aws ecr create-repository --repository-name employees-system

# الحصول على رابط تسجيل الدخول
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account-id.dkr.ecr.us-east-1.amazonaws.com
```

#### ب. بناء ورفع Docker Image
```bash
# بناء الصورة
docker build -t employees-system .

# وضع علامة على الصورة
docker tag employees-system:latest your-account-id.dkr.ecr.us-east-1.amazonaws.com/employees-system:latest

# رفع الصورة إلى ECR
docker push your-account-id.dkr.ecr.us-east-1.amazonaws.com/employees-system:latest
```

### الخطوة 5: النشر باستخدام Elastic Beanstalk

#### أ. إنشاء التطبيق
```bash
# تهيئة EB في المجلد
eb init employees-system --region us-east-1 --platform "Python 3.9"

# إنشاء البيئة
eb create employees-prod --instance-type t3.micro
```

#### ب. تكوين متغيرات البيئة
```bash
# تعيين متغيرات البيئة
eb setenv FLASK_ENV=production \
         SECRET_KEY=your_secret_key \
         DATABASE_URL=postgresql://admin:password@your-rds-endpoint:5432/postgres \
         AWS_ACCESS_KEY_ID=your_key \
         AWS_SECRET_ACCESS_KEY=your_secret \
         S3_BUCKET=your-bucket-name
```

#### ج. النشر
```bash
# نشر التطبيق
eb deploy

# فتح التطبيق في المتصفح
eb open
```

### الخطوة 6: إعداد قاعدة البيانات

1. الاتصال بقاعدة البيانات وإنشاء قاعدة البيانات:
```sql
CREATE DATABASE employees_db;
```

2. تشغيل migration لإنشاء الجداول:
```bash
# الاتصال بالخادم عبر SSH
eb ssh

# تشغيل Python shell
python

# في Python shell
from app import app, db
with app.app_context():
    db.create_all()
```

## البدائل الأخرى للنشر

### 1. AWS Lambda + API Gateway
- استخدم Zappa لنشر Flask كـ serverless
- مناسب للتطبيقات الصغيرة

### 2. AWS ECS (Elastic Container Service)
- استخدم Docker containers
- مناسب للتطبيقات الكبيرة

### 3. AWS EC2
- نشر مباشر على خادم EC2
- تحكم كامل في البيئة

## مراقبة التطبيق

### CloudWatch Logs
```bash
# عرض logs التطبيق
eb logs

# متابعة logs في الوقت الفعلي
eb logs --all
```

### Health Monitoring
```bash
# فحص حالة التطبيق
eb health

# عرض معلومات مفصلة
eb status
```

## الأمان

### 1. SSL Certificate
- استخدم AWS Certificate Manager
- قم بتكوين HTTPS

### 2. Security Groups
- قم بتقييد الوصول للمنافذ المطلوبة فقط
- استخدم VPC للعزل

### 3. IAM Roles
- أنشئ IAM roles محددة للتطبيق
- اتبع مبدأ الصلاحيات الأدنى

## استكشاف الأخطاء

### مشاكل شائعة:

1. **خطأ في الاتصال بقاعدة البيانات**
   - تحقق من security groups
   - تأكد من صحة connection string

2. **مشاكل في متغيرات البيئة**
   - تحقق من تعيين المتغيرات في EB
   - استخدم `eb printenv` لعرض المتغيرات

3. **مشاكل في الذاكرة**
   - قم بترقية instance type
   - راقب استخدام الذاكرة في CloudWatch

## التكاليف المتوقعة

- **t3.micro EC2**: ~$8.5/شهر
- **RDS t3.micro**: ~$13/شهر
- **S3 Storage**: ~$0.023/GB/شهر
- **Data Transfer**: متغير حسب الاستخدام

**إجمالي تقديري**: ~$25-30/شهر للاستخدام الأساسي

## الدعم

للحصول على المساعدة:
1. راجع AWS Documentation
2. استخدم AWS Support (إذا كان لديك خطة دعم)
3. راجع CloudWatch Logs للأخطاء

---

**ملاحظة**: تأكد من حفظ جميع المعلومات الحساسة (كلمات المرور، مفاتيح API) في مكان آمن ولا تشاركها في الكود المصدري.