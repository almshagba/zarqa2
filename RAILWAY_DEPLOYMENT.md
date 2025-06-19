# نشر نظام شؤون الموظفين على Railway

## المتطلبات الأساسية
- حساب على [Railway](https://railway.app)
- Git مثبت على جهازك
- Railway CLI (اختياري)

## خطوات النشر

### 1. إعداد المشروع على Railway

#### الطريقة الأولى: من خلال GitHub (الأسهل)
1. ارفع المشروع إلى GitHub repository
2. اذهب إلى [Railway Dashboard](https://railway.app/dashboard)
3. اضغط على "New Project"
4. اختر "Deploy from GitHub repo"
5. اختر المستودع الخاص بك

#### الطريقة الثانية: Railway CLI
```bash
# تثبيت Railway CLI
npm install -g @railway/cli

# تسجيل الدخول
railway login

# إنشاء مشروع جديد
railway init

# نشر المشروع
railway up
```

### 2. إضافة قاعدة البيانات PostgreSQL
1. في Railway Dashboard، اضغط على "+ New"
2. اختر "Database" ثم "PostgreSQL"
3. سيتم إنشاء قاعدة البيانات تلقائياً
4. Railway سيقوم بربط قاعدة البيانات بالتطبيق تلقائياً

### 3. تكوين متغيرات البيئة
في Railway Dashboard، اذهب إلى Variables وأضف:

```
FLASK_ENV=production
SECRET_KEY=your_very_secure_secret_key_here
PORT=5000
```

**ملاحظة:** `DATABASE_URL` سيتم إضافته تلقائياً بواسطة Railway

### 4. إعدادات اختيارية (AWS S3)
إذا كنت تستخدم AWS S3 لتخزين الملفات:
```
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
S3_BUCKET=your_bucket_name
```

### 5. النشر
بعد إعداد كل شيء:
1. Railway سيقوم بالنشر تلقائياً
2. ستحصل على رابط التطبيق
3. يمكنك الوصول إلى التطبيق من الرابط المقدم

## إدارة قاعدة البيانات

### إنشاء الجداول الأولية
بعد النشر الأول، ستحتاج لإنشاء الجداول:

```python
# يمكنك تشغيل هذا من Railway Console أو محلياً
from app import app, db
with app.app_context():
    db.create_all()
```

### الوصول إلى قاعدة البيانات
- يمكنك الوصول إلى قاعدة البيانات من Railway Dashboard
- استخدم أدوات مثل pgAdmin أو DBeaver
- معلومات الاتصال متوفرة في Variables

## الملفات المهمة للنشر

- `requirements.txt` - متطلبات Python
- `Procfile` - أمر تشغيل التطبيق
- `runtime.txt` - إصدار Python
- `railway.json` - إعدادات Railway
- `wsgi.py` - نقطة دخول التطبيق

## استكشاف الأخطاء

### مشاكل شائعة:

1. **خطأ في قاعدة البيانات**
   - تأكد من إضافة PostgreSQL service
   - تحقق من متغير DATABASE_URL

2. **خطأ في التطبيق**
   - راجع Logs في Railway Dashboard
   - تأكد من SECRET_KEY

3. **مشاكل الملفات الثابتة**
   - تأكد من مجلد static موجود
   - راجع إعدادات UPLOAD_FOLDER

### عرض السجلات
```bash
# باستخدام Railway CLI
railway logs
```

أو من Railway Dashboard > Deployments > View Logs

## الصيانة والتحديث

### تحديث التطبيق
- ادفع التغييرات إلى GitHub
- Railway سيقوم بالنشر تلقائياً

### النسخ الاحتياطي
- Railway يقوم بنسخ احتياطي تلقائي لقاعدة البيانات
- يمكنك تصدير البيانات يدوياً من Dashboard

## الأمان

- استخدم SECRET_KEY قوي ومعقد
- لا تشارك متغيرات البيئة
- راجع صلاحيات المستخدمين بانتظام
- استخدم HTTPS (Railway يوفره تلقائياً)

## الدعم

- [Railway Documentation](https://docs.railway.app)
- [Railway Discord](https://discord.gg/railway)
- [Railway GitHub](https://github.com/railwayapp)

---

**ملاحظة:** تأكد من تحديث جميع كلمات المرور والمفاتيح السرية قبل النشر في الإنتاج.