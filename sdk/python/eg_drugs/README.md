# eg-drugs Python SDK

مكتبة Python للوصول إلى قاعدة بيانات الأدوية المصرية (**eg-drugs**) — 27,617+ دواء marketed في مصر.

## التثبيت

```bash
pip install -e sdk/python/eg_drugs
```

أو مباشرة من GitHub:

```bash
pip install git+https://github.com/abduallahJamal/eg-drugs.git#subdirectory=sdk/python/eg_drugs
```

## الاستخدام السريع

```python
from eg_drugs import search, get_by_id, get_by_barcode, get_generics, load_stats

# بحث بالاسم (عربي أو إنجليزي)
results = search("panadol", limit=5)
for drug in results:
    print(drug.arabic, "-", drug.price, "ج.م")

# جلب دواء بالمعرف
drug = get_by_id(1)
print(drug.arabic, drug.active)

# جلب دواء بالباركود
drug = get_by_barcode("6221000003295")
print(drug.name, drug.company)

# الأدوية البديلة (نفس المادة الفعالة)
generics = get_generics("paracetamol", limit=10)
for g in generics:
    print(g.arabic, g.price)

# إحصائيات قاعدة البيانات
stats = load_stats()
print(f"إجمالي الأدوية: {stats.total_drugs:,}")
print(f"الشركات: {stats.unique_companies}")
print(f"المواد الفعالة: {stats.unique_active_ingredients}")
```

## العمل مع واجهة برمجة التطبيقات (API) عن بعد

إذا كان لديك خادم API يعمل على عنوان معين:

```python
from eg_drugs import EgDrugsClient

client = EgDrugsClient(base_url="https://api.example.com")
results = client.search("بانادول", limit=10)
```

## العمل مع الملفات المحلية

بشكل افتراضي، تبحث المكتبة في ملف `data/eg_drugs.sqlite` الموجود في المستودع. يمكنك تحديد مسار مخصص:

```python
from eg_drugs import EgDrugsClient

client = EgDrugsClient(db_path="/path/to/eg_drugs.sqlite")
results = client.search("panadol")
```

## الترخيص

MIT License — راجع ملف `LICENSE-MIT` في جذر المستودع.
