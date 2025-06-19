import pandas as pd

# Create sample data
data = {
    'رقم الموظف': ['EMP001', 'EMP002'],
    'الاسم': ['احمد محمد', 'سارة احمد'],
    'المنصب': ['مدير', 'محاسب'],
    'القسم': ['الإدارة', 'المالية'],
    'تاريخ التعيين': ['2023-01-01', '2023-02-01'],
    'رقم الهاتف': ['0501234567', '0501234568'],
    'البريد الإلكتروني': ['ahmed@example.com', 'sara@example.com']
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel
df.to_excel('نموذج_بيانات_الموظفين.xlsx', index=False)
print("تم إنشاء نموذج ملف الإكسل بنجاح!") 