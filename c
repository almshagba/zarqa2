eport_all_employees.html
{% extends 'base.html' %}

{% block head_extra %}
<!-- مكتبات تصدير البيانات -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.5.28/jspdf.plugin.autotable.min.js"></script>
<!-- إضافة خط عربي لدعم اللغة العربية في PDF -->
<script src="https://cdn.jsdelivr.net/npm/amiri-font@1.0.0/amiri.min.js"></script>
<!-- تحميل احتياطي لخط Amiri -->
<script>
    // التحقق من تحميل خط Amiri
    window.addEventListener('load', function() {
        if (typeof window.AmiriFont === 'undefined') {
            console.warn('تحميل خط Amiri من المصدر الاحتياطي...');
            // تحميل الخط من مصدر بديل
            var amiriScript = document.createElement('script');
            amiriScript.src = "https://cdn.jsdelivr.net/npm/@khmyznikov/pdfmake-fonts@1.0.0/build/amiri/index.js";
            document.head.appendChild(amiriScript);
            
            amiriScript.onload = function() {
                if (typeof window.pdfMake !== 'undefined' && 
                    typeof window.pdfMake.vfs !== 'undefined' && 
                    typeof window.pdfMake.vfs['amiri-normal.ttf'] !== 'undefined') {
                    window.AmiriFont = window.pdfMake.vfs['amiri-normal.ttf'];
                    console.log('تم تحميل خط Amiri بنجاح من المصدر البديل');
                }
            };
        }
    });
</script>
{% endblock %}

// دالة تصدير البيانات إلى PDF
function exportToPDF() {
    if (document.getElementById('employeesTable').rows.length <= 1) {
        alert('لا توجد بيانات للتصدير');
        return;
    }
    
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF('l', 'mm', 'a4', true); // landscape orientation
    
    // التحقق من توفر الخط قبل استخدامه
    if (typeof window.AmiriFont === 'undefined') {
        alert('خطأ: لم يتم تحميل خط Amiri بشكل صحيح. سيتم استخدام الخط الافتراضي.');
        // استخدام الخط الافتراضي
        doc.setFont('Helvetica');
    } else {
        // إضافة دعم للغة العربية
        doc.addFileToVFS('Amiri-Regular.ttf', window.AmiriFont);
        doc.addFont('Amiri-Regular.ttf', 'Amiri', 'normal', 'Identity-H');
        doc.setFont('Amiri');
    }
    
    const title = "تقرير شامل لجميع الموظفين";
    const fileName = `تقرير_شامل_للموظفين_${new Date().toISOString().slice(0,10)}.pdf`;
    
    // إضافة العنوان
    doc.setFontSize(18);
    doc.text(title, doc.internal.pageSize.width / 2, 20, { 
        align: 'center',
        isInputRtl: true,  // تحديد أن النص من اليمين إلى اليسار
        isOutputRtl: true  // إضافة هذا الخيار لضمان إخراج النص من اليمين إلى اليسار
    });
    
    // إنشاء الجدول
    doc.autoTable({
        html: '#employeesTable',
        startY: 30,
        theme: 'grid',
        headStyles: { fillColor: [41, 128, 185], textColor: 255, font: doc.getFont().fontName },
        styles: { 
            halign: 'right', 
            font: doc.getFont().fontName,
            direction: 'rtl',  // تحديد اتجاه النص من اليمين إلى اليسار
            minCellWidth: 20   // تحديد الحد الأدنى لعرض الخلية
        },
        margin: { top: 30 },
});
outes\employee_routes.py
    # الحصول على قائمة الموظفين مع إمكانية البحث والتصفية
    search_term = request.args.get('search', '')
    job_filter = request.args.get('job_title', '')
    school_filter = request.args.get('school_id', '')
    
    # تصفية الموظفين لإظهار موظفي المدارس فقط (ليس موظفي المديرية)
    query = Employee.query.filter_by(is_directorate_employee=False)
    
    if search_term:
        query = query.filter(
            db.or_(
                Employee.name.ilike(f'%{search_term}%'),
                Employee.ministry_number.ilike(f'%{search_term}%'),
                Employee.civil_id.ilike(f'%{search_term}%')
            )
        )