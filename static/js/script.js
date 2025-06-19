// ملف JavaScript مخصص للتطبيق

// وظائف عامة للنظام

// عرض الرسائل للمستخدم
function showMessage(message, type = 'info') {
    // إزالة الرسائل السابقة
    const existingMessages = document.querySelectorAll('.message');
    existingMessages.forEach(msg => msg.remove());
    
    // إنشاء رسالة جديدة
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = message;
    
    // إضافة الرسالة في أعلى الصفحة
    const container = document.querySelector('.container-fluid') || document.body;
    container.insertBefore(messageDiv, container.firstChild);
    
    // إخفاء الرسالة بعد 5 ثوان
    setTimeout(() => {
        messageDiv.remove();
    }, 5000);
}

// تأكيد الحذف
function confirmDelete(message = 'هل أنت متأكد من الحذف؟') {
    return window.confirm(message);
}

// تحسين تجربة المستخدم للنماذج
document.addEventListener('DOMContentLoaded', function() {
    // تم إزالة الكود المتداخل مع تأكيد الحذف لتجنب التداخل مع النماذج
    
    // تحسين النماذج
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = 'جاري المعالجة...';
            }
        });
    });
});

// وظائف مساعدة للتصدير
function showLoading(show = true) {
    const loadingDiv = document.getElementById('loadingDiv');
    if (loadingDiv) {
        if (show) {
            loadingDiv.classList.add('show');
        } else {
            loadingDiv.classList.remove('show');
        }
    }
}

// نسخ النص إلى الحافظة
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showMessage('تم نسخ النص إلى الحافظة', 'success');
        }).catch(() => {
            fallbackCopyToClipboard(text);
        });
    } else {
        fallbackCopyToClipboard(text);
    }
}

function fallbackCopyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.select();
    try {
        document.execCommand('copy');
        showMessage('تم نسخ النص إلى الحافظة', 'success');
    } catch (err) {
        showMessage('فشل في نسخ النص', 'error');
    }
    document.body.removeChild(textArea);
}

// دالة للتحقق من حالة الشبكة
function checkNetworkStatus() {
    if (!navigator.onLine) {
        showMessage('تحذير: لا يوجد اتصال بالإنترنت. قد لا تعمل بعض الوظائف بشكل صحيح.', 'warning');
    }
}

// فحص حالة الشبكة عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    checkNetworkStatus();
    
    // مراقبة تغيير حالة الشبكة
    window.addEventListener('online', function() {
        showMessage('تم استعادة الاتصال بالإنترنت', 'success', 3000);
    });
    
    window.addEventListener('offline', function() {
        showMessage('تم فقدان الاتصال بالإنترنت', 'warning');
    });
});