# eg-drugs Node.js SDK

مكتبة Node.js للوصول إلى قاعدة بيانات الأدوية المصرية (**eg-drugs**) — 27,617+ دواء marketed في مصر.

## التثبيت

```bash
npm install
```
(داخل مجلد `sdk/node/eg-drugs`)

أو مباشرة من GitHub:

```bash
npm install git+https://github.com/abduallahJamal/eg-drugs.git#subdirectory=sdk/node/eg-drugs
```

## الاستخدام السريع

```js
const { search, getById, getByBarcode, getGenerics, loadStats } = require('eg-drugs');

// بحث بالاسم (عربي أو إنجليزي)
const results = await search('panadol', { limit: 5 });
for (const drug of results) {
  console.log(drug.arabic, '-', drug.price, 'ج.م');
}

// جلب دواء بالمعرف
const drug = await getById(1);
console.log(drug.arabic, drug.active);

// جلب دواء بالباركود
const drug2 = await getByBarcode('6221000003295');
console.log(drug2.name, drug2.company);

// الأدوية البديلة (نفس المادة الفعالة)
const generics = await getGenerics('paracetamol', { limit: 10 });
for (const g of generics) {
  console.log(g.arabic, g.price);
}

// إحصائيات قاعدة البيانات
const stats = await loadStats();
console.log(`إجمالي الأدوية: ${stats.totalDrugs.toLocaleString()}`);
console.log(`الشركات: ${stats.uniqueCompanies}`);
console.log(`المواد الفعالة: ${stats.uniqueActiveIngredients}`);
```

## العمل مع واجهة برمجة التطبيقات (API) عن بعد

```js
const { EgDrugsClient } = require('eg-drugs');

const client = new EgDrugsClient({ baseUrl: 'https://api.example.com' });
const results = await client.search('بانادول', { limit: 10 });
```

## العمل مع الملفات المحلية

بشكل افتراضي، تبحث المكتبة في ملف `data/eg_drugs.sqlite` الموجود في المستودع.
يمكنك تحديد مسار مخصص:

```js
const client = new EgDrugsClient({ dbPath: '/path/to/eg_drugs.sqlite' });
const results = await client.search('panadol');
```

## المتطلبات

- Node.js >= 18
- أمر `sqlite3` سطر الأوامر مثبت على النظام (للعمل المحلي السريع).
  إذا لم يكن مثبتًا، تعود المكتبة تلقائيًا إلى قراءة ملف JSON.

## الترخيص

MIT License — راجع ملف `LICENSE-MIT` في جذر المستودع.
