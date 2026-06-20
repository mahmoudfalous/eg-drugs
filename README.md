# Egyptian Drug Database (`eg_drugs`)

This directory contains the cleaned, standardized, and FDA-enriched database of drugs marketed in Egypt. It consists of two complementary files located in the `data/` directory: `eg_drugs.csv` and `eg_drugs.json`. 

Both files contain exactly **26,562 records** and share the **exact same schema**, featuring localized summaries, chemical classifications, and safety warning flags.

---

## Files Overview

### 1. `data/eg_drugs.csv`
* **Format**: CSV (Comma Separated Values)
* **Size**: ~22.1 MB
* **Use Case**: Ideal for lightweight data analysis, importing into databases (e.g., PostgreSQL, SQLite), and tabular data workflows.
* **Encoding**: UTF-8

### 2. `data/eg_drugs.json`
* **Format**: JSON Array of Objects
* **Size**: ~36.5 MB
* **Use Case**: Ideal for application runtime delivery (APIs, web apps, mobile apps). 
* **Encoding**: UTF-8
* *Note on Size*: The JSON file is larger because field names/keys are repeated in every object, whereas the CSV defines them once in the header.

---

## Schema Definition

Both files contain the following fields:

| Field Name | Type (CSV) | Type (JSON) | Description |
| :--- | :--- | :--- | :--- |
| `id` | String | Integer | Unique identifier for each drug record. |
| `name` | String | String | Commercial/Brand name of the drug in English. |
| `arabic` | String | String | Commercial/Brand name of the drug in Arabic. |
| `active` | String | String | Active ingredients/compounds (joined by `+`). |
| `company` | String | String | Manufacturing or distributing pharmaceutical company. |
| `price` | String | String | Current retail price in EGP (may contain trailing dot format). |
| `oldprice` | String | String | Previous retail price in EGP (for tracking price changes). |
| `availability` | String/Empty | Int/Null | Stock quantity or availability indicator. |
| `barcode` | String | String | Standard barcode number (EAN/UPC). |
| `slug` | String | String | URL-friendly unique slug. |
| `units` | String | Int/Null | Pack units/size count. |
| `description` | String | String | General category (e.g., "Cold drugs"). |
| `uses` | String | String | Detailed indications of usage in Arabic (paragraph text). |
| `matched_fda_ingredients` | String | String | Ingredients mapped to official FDA entries (joined by ` \| `). |
| `uses_summary` | String | String | Short Arabic summary of uses (extracted from the detailed description). |
| `uses_summary_en` | String | String | Short English summary of uses (extracted from FDA data). |
| `warning_high_blood_pressure` | Integer (0/1) | Integer (0/1) | Alert flag for patients with hypertension. |
| `warning_diabetes` | Integer (0/1) | Integer (0/1) | Alert flag for patients with diabetes. |
| `warning_pregnancy` | Integer (0/1) | Integer (0/1) | Alert flag for pregnancy risk (teratogenic / contraindications). |
| `warning_lactation` | Integer (0/1) | Integer (0/1) | Alert flag for breastfeeding risks. |
| `warning_kidney` | Integer (0/1) | Integer (0/1) | Alert flag for patients with renal impairment. |
| `warning_liver` | Integer (0/1) | Integer (0/1) | Alert flag for patients with hepatic impairment. |
| `warning_heart` | Integer (0/1) | Integer (0/1) | Alert flag for patients with heart/cardiovascular disease. |
| `warnings_summary` | String | String | Synthesized list of warnings in Arabic. |
| `warnings_summary_en` | String | String | Synthesized list of warnings in English. |

---

## Data Samples

### 1. `data/eg_drugs.csv` (First Row Representation)

```json
{
  "id": "1",
  "name": "1 2 3 (one two three) syrup 120 ml",
  "arabic": "ون تو ثري شراب 120 مل",
  "active": "Chlorpheniramine+paracetamol+pseudoephedrine",
  "company": "Hikma",
  "price": "40.00.",
  "oldprice": "32.00.",
  "availability": "",
  "barcode": "6221000000010",
  "slug": "1",
  "units": "1",
  "description": "Cold drugs",
  "uses": "تخفيف أعراض نزلات البرد والإنفلونزا مثل الصداع وارتفاع درجة الحرارة. يساعد في علاج احتقان الأنف والجيوب الأنفية وتحسين التنفس. يخفف سيلان الأنف والعطس الناتج عن الحساسية أو البرد. يقلل آلام الجسم والعضلات المصاحبة لنزلات البرد. يساعد على تهدئة الصداع المرتبط بالبرد أو احتقان الجيوب الأنفية. يساهم في تقليل احمرار ودموع العين الناتجة عن الحساسية. يستخدم لتخفيف أعراض الحساسية الموسمية المصحوبة باحتقان وسيلان الأنف.",
  "matched_fda_ingredients": "pseudoephedrine | chlorpheniramine",
  "uses_summary": "تخفيف أعراض نزلات البرد والإنفلونزا مثل الصداع وارتفاع درجة الحرارة. يساعد في علاج احتقان الأنف والجيوب الأنفية وتحسين التنفس.",
  "uses_summary_en": "temporarily relieves nasal congestion due to the common cold, hay fever or other upper respiratory allergies temporarily relieves sinus congestion and pressure || Uses temporarily relieves these symptoms due to hay fever (allergic rhinitis) or other upper respiratory allergies: sneezing runny nose itching of the nose or throat itchy, watery eyes.",
  "warning_high_blood_pressure": "1",
  "warning_diabetes": "1",
  "warning_pregnancy": "1",
  "warning_lactation": "1",
  "warning_kidney": "0",
  "warning_liver": "0",
  "warning_heart": "1",
  "warnings_summary": "يحذر أو يوصى بالحذر تحت إشراف طبي في الحالات التالية: الحمل، الرضاعة الطبيعية، ارتفاع ضغط الدم، مرض السكري، أمراض القلب.",
  "warnings_summary_en": "Caution or warning advised under medical supervision for: Pregnancy, Lactation/Breastfeeding, High Blood Pressure, Diabetes, Heart Disease."
}
```

### 2. `data/eg_drugs.json` (First Item Representation)

```json
{
  "id": 1,
  "name": "1 2 3 (one two three) syrup 120 ml",
  "arabic": "ون تو ثري شراب 120 مل",
  "active": "Chlorpheniramine+paracetamol+pseudoephedrine",
  "company": "Hikma",
  "price": "40.00.",
  "oldprice": "32.00.",
  "availability": null,
  "barcode": "6221000000010",
  "slug": "1",
  "units": 1,
  "description": "Cold drugs",
  "uses": "تخفيف أعراض نزلات البرد والإنفلونزا مثل الصداع وارتفاع درجة الحرارة. يساعد في علاج احتقان الأنف والجيوب الأنفية وتحسين التنفس. يخفف سيلان الأنف والعطس الناتج عن الحساسية أو البرد. يقلل آلام الجسم والعضلات المصاحبة لنزلات البرد. يساعد على تهدئة الصداع المرتبط بالبرد أو احتقان الجيوب الأنفية. يساهم في تقليل احمرار ودموع العين الناتجة عن الحساسية. يستخدم لتخفيف أعراض الحساسية الموسمية المصحوبة باحتقان وسيلان الأنف.",
  "matched_fda_ingredients": "pseudoephedrine | chlorpheniramine",
  "uses_summary": "تخفيف أعراض نزلات البرد والإنفلونزا مثل الصداع وارتفاع درجة الحرارة. يساعد في علاج احتقان الأنف والجيوب الأنفية وتحسين التنفس.",
  "uses_summary_en": "temporarily relieves nasal congestion due to the common cold, hay fever or other upper respiratory allergies temporarily relieves sinus congestion and pressure || Uses temporarily relieves these symptoms due to hay fever (allergic rhinitis) or other upper respiratory allergies: sneezing runny nose itching of the nose or throat itchy, watery eyes.",
  "warning_high_blood_pressure": 1,
  "warning_diabetes": 1,
  "warning_pregnancy": 1,
  "warning_lactation": 1,
  "warning_kidney": 0,
  "warning_liver": 0,
  "warning_heart": 1,
  "warnings_summary": "يحذر أو يوصى بالحذر تحت إشراف طبي في الحالات التالية: الحمل، الرضاعة الطبيعية، ارتفاع ضغط الدم، مرض السكري، أمراض القلب.",
  "warnings_summary_en": "Caution or warning advised under medical supervision for: Pregnancy, Lactation/Breastfeeding, High Blood Pressure, Diabetes, Heart Disease."
}
```

---

## Loading and Usage Guidelines

### Python (CSV)
```python
import csv

with open('data/eg_drugs.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(f"Drug: {row['name']} | Price: {row['price']}")
        break
```

### Python (JSON)
> [!IMPORTANT]
> The source active ingredients text contains some literal raw control characters (e.g., `\x08` backspace) from scraping. When parsing the JSON file in strict environments (such as Python's standard `json` library or JavaScript's `JSON.parse`), you should pass `strict=False` or clean the string to avoid `JSONDecodeError`.

```python
import json

# Correct way to parse JSON containing control characters in Python:
with open('data/eg_drugs.json', encoding='utf-8') as f:
    drugs = json.load(f, strict=False)

print(f"Total drugs: {len(drugs)}")
print(f"First drug warnings: {drugs[0]['warnings_summary']}")
```

### JavaScript / Node.js (JSON)
```javascript
const fs = require('fs');

// Read and sanitize control characters before parsing:
let jsonString = fs.readFileSync('data/eg_drugs.json', 'utf8');
// Replace control characters (except tabs and newlines if desired)
jsonString = jsonString.replace(/[\x00-\x1F\x7F-\x9F]/g, " ");

const drugs = JSON.parse(jsonString);
console.log(`Loaded ${drugs.length} drugs.`);
```

---

## License & Contact

* **Usage**: You are free to use this database in any unpaid (non-commercial) projects.
* **Last Updated**: 21 Jun 2026
* **Contact**: Feel free to reach out via email at [mahmoudfalous@gmail.com](mailto:mahmoudfalous@gmail.com).

