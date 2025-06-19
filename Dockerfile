FROM python:3.11-slim

# تعيين متغيرات البيئة
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=wsgi.py
ENV FLASK_ENV=production

# إنشاء مستخدم غير جذر للأمان
RUN groupadd -r appuser && useradd -r -g appuser appuser

# إنشاء مجلد العمل
WORKDIR /app

# تثبيت متطلبات النظام
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# نسخ ملف المتطلبات وتثبيتها
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# نسخ كود التطبيق
COPY . .

# إنشاء مجلدات ضرورية
RUN mkdir -p /app/instance /app/static/uploads \
    && chown -R appuser:appuser /app

# التبديل للمستخدم غير الجذر
USER appuser

# فتح المنفذ
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# تشغيل التطبيق باستخدام Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "wsgi:app"]