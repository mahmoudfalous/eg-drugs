# Egyptian Drug Database (`eg_drugs`)

A clean, standardized, and continuously updated pharmaceutical database containing **27,617+ drugs marketed in Egypt**, including active ingredients, commercial names in Arabic and English, current and previous retail prices (`price` and `oldprice`), manufacturers, barcodes, and medical categories.

All files are located in the `data/` directory and available in **CSV**, **JSON**, **SQLite**, and **SQL dump** formats.

---

## 🚀 جديد في هذا الفرع (التطويرات المضافة)

| المكون | المسار | الوصف |
|--------|-------|-------|
| **REST API** | `api/main.py` | واجهة برمجة تطبيقات بـ FastAPI للبحث في الأدوية، الباركود، والأدوية البديلة |
| **واجهة ويب** | `web/index.html` | واجهة بحث عربية تفاعلية تتصل بـ API |
| **مكتبة Python** | `sdk/python/eg_drugs` | حزمة Python لاستيراد والبحث في البيانات برمجياً |
| **مكتبة Node.js** | `sdk/node/eg-drugs` | حزمة Node.js للمطورين |
| **أدوات جودة البيانات** | `tools/` | سكريبتات للتحقق من سلامة البيانات والباركود |
| **اختبارات** | `tests/` | اختبارات لوحدة البيانات وواجهة API |
| **Docker** | `Dockerfile` | حاوية تشغيل سريعة لـ API |
| **إجراءات CI** | `.github/workflows/ci.yml` | فحص تلقائي للبناء والاختبارات عند كل Pull Request |

---

## 📂 نظرة عامة على الملفات

| الملف | الصيغة | الحجم | الوصف |
|-------|--------|------|-------|
| `data/eg_drugs.csv` | CSV (UTF-8) | ~8.1 MB | بيانات مفصولة بفاصلة لـ Pandas، إكسل، أو خطوط ETL |
| `data/eg_drugs.json` | JSON Array | ~16 MB | مصفوفة من كائنات الأدوية لتطبيقات الويب والجوال وواجهات API |
| `data/eg_drugs.sqlite` | SQLite DB | ~13 MB | قاعدة بيانات علائقية مع فهارس مبنية على `name`, `arabic`, `active`, و `barcode` |
| `data/eg_drugs.sql` | SQL Dump | ~9.7 MB | dumped SQL متوافق مع SQLite، PostgreSQL، و MySQL |

---

## 🧱 المخطط (Schema)

| اسم الحقل | النوع (SQL/CSV) | النوع (JSON) | الوصف |
|-----------|-----------------|--------------|-------|
| `id` | INTEGER PRIMARY KEY | Integer | معرف فريد لكل سجل دواء |
| `name` | TEXT | String | الاسم التجاري بالإنجليزية |
| `arabic` | TEXT | String | الاسم التجاري بالعربية |
| `active` | TEXT | String | المواد الفعالة/المركبات الدوائية |
| `company` | TEXT | String | الشركة المصنعة أو الموزعة |
| `price` | TEXT | String | سعر التجزئة الحالي بالجنيه المصري |
| `oldprice` | TEXT | String | سعر التجزئة السابق (لتتبع تحديثات الأسعار) |
| `barcode` | TEXT | String | رقم الباركود (EAN/GTIN) |
| `barcode_valid` | TEXT (0/1) | String ("0"/"1") | علامة التحقق من صحة GS1 (`1` = صحيح، `0` = غير صحيح/غائب) |
| `slug` | TEXT | String | معرف ودود للرابط (URL-friendly) |
| `units` | TEXT | String | عدد وحدات التغليف / حجم العبوة |
| `description` | TEXT | String | تصنيف الدواء (مثلاً: `cold products`, `antineoplastic`) |
| `uses` | TEXT | String | الاستخدامات وال응اءة العلاجية بالعربية |

---

## 🔌 واجهة برمجة التطبيقات (REST API)

### التشغيل المحلي
```bash
# تثبيت التبعيات
pip install -r api/requirements.txt

# تشغيل الخادم
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### توثيق تفاعلي
بعد التشغيل، افتح: `http://localhost:8000/docs`

### النقاط النهائية (Endpoints)

| الطريقة | النقطة | الوصف |
|--------|--------|-------|
| `GET` | `/` | معلومات API والنقاط المتاحة |
| `GET` | `/drugs/search?q=كلمة` | بحث بالأسماء العربية/الإنجليزية، المواد الفعالة، أو الشركات |
| `GET` | `/drugs/{id}` | جلب دواء بالمعرف الرقمي |
| `GET` | `/drugs/barcode/{barcode}` | جلب دواء برقم الباركود |
| `GET` | `/drugs/generics/{active}` | جلب الأدوية البديلة (نفس المادة الفعالة) |
| `GET` | `/categories` | قائمة التصنيفات الطبية |
| `GET` | `/companies` | قائمة الشركات المصنعة |
| `GET` | `/stats` | إحصائيات قاعدة البيانات |
| `GET` | `/health` | فحص حالة الخدمة |

### مثال على البحث
```bash
curl "http://localhost:8000/drugs/search?q=panadol&limit=5"
```

---

## 🖥️ واجهة الويب (Search UI)

افتح `web/index.html` في المتصفح، أو شغّل الخادم أعلاه وزور `http://localhost:8000` لعرض واجهة البحث العربية المتكاملة.

---

## 📦 المكتبات البرمجية (SDKs)

### Python
```bash
cd sdk/python/eg_drugs
pip install -e .
```
```python
from eg_drugs import search

results = search("panadol", lang="ar")
for drug in results:
    print(drug["arabic"], drug["price"])
```

### Node.js
```bash
cd sdk/node/eg-drugs
npm install
```
```js
const { search } = require('eg-drugs');
const results = await search('panadol');
console.log(results);
```

---

## 🛠️ أدوات جودة البيانات

يحتوي مجلد `tools/` على سكريبتات لـ:
- التحقق من صحة الباركود (GS1 checksum)
- البحث عن سجلات مكررة أو ناقصة الحقول الأساسية
- اكتشاف اختلافات كبيرة في الأسعار بين `price` و `oldprice`

---

## 🐳 Docker

```bash
docker build -t eg-drugs-api .
docker run -p 8000:8000 eg-drugs-api
```

---

## 🔁 التكامل المستمر (CI)

سير عمل GitHub Actions (`ci.yml`) يشغّل:
1. `pip install -r api/requirements.txt`
2. بناء وفحص واجهة API
3. تشغيل الاختبارات في `tests/`

عند كل push أو Pull Request إلى الفرع `main`.

---

## 📜 التراخيص

- **الكود:** MIT License (`LICENSE-MIT`)
- **البيانات:** CC-BY-4.0 (`LICENSE-DATA`)

---

## 🤝 المساهمة

مرحباً بالمساهمات! يمكنك Fork المستودع، إجراء التعديلات، وإرسال Pull Request. يرجى الاطلاع على `CODE_OF_CONDUCT.md` قبل المساهمة.
