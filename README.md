# Egyptian Drug Database (26K+ Drugs)

A comprehensive, FDA-enriched pharmaceutical dataset containing **26,562 drugs marketed in Egypt**, including active ingredients, Arabic and English drug information, FDA ingredient mapping, localized usage summaries, and medical safety warning flags.

This dataset was created to support healthcare applications, pharmacy systems, AI assistants, search engines, data analysis, and academic research involving Egyptian pharmaceutical products.

---

## Dataset Statistics

| Metric | Value |
|----------|----------|
| Total Drug Records | 26,562 |
| Languages | Arabic + English |
| FDA Ingredient Mapping | Included |
| Safety Warning Flags | Included |
| Formats Available | CSV, JSON |
| Last Updated | 21 Jun 2026 |

---

## Files Overview

### `data/eg_drugs.csv`

- **Format:** CSV (Comma Separated Values)
- **Size:** ~22.1 MB
- **Encoding:** UTF-8
- **Ideal for:**
  - PostgreSQL
  - MySQL
  - SQLite
  - Pandas
  - Data Analysis

### `data/eg_drugs.json`

- **Format:** JSON Array
- **Size:** ~36.5 MB
- **Encoding:** UTF-8
- **Ideal for:**
  - APIs
  - Web Applications
  - Mobile Applications
  - AI Systems
  - Search Engines

> JSON is larger because field names are repeated for every object.

---

## Data Processing Pipeline

The dataset was built through a multi-stage processing pipeline:

1. Collection of Egyptian pharmaceutical product records.
2. Data cleaning and normalization.
3. Standardization of drug names and company names.
4. Active ingredient extraction.
5. FDA ingredient matching.
6. Generation of Arabic usage descriptions.
7. Generation of Arabic usage summaries.
8. Extraction of English FDA-based summaries.
9. Safety warning detection.
10. Export to CSV and JSON formats.

---

## Schema

| Field | Description |
|---------|---------|
| id | Unique drug identifier |
| name | Drug name (English) |
| arabic | Drug name (Arabic) |
| active | Active ingredients |
| company | Manufacturer or distributor |
| price | Current retail price |
| oldprice | Previous retail price |
| availability | Availability indicator |
| barcode | Drug barcode |
| slug | URL-friendly identifier |
| units | Package units |
| description | Drug category |
| uses | Detailed Arabic usage description |
| matched_fda_ingredients | FDA-matched ingredients |
| uses_summary | Short Arabic summary |
| uses_summary_en | Short English summary |
| warning_high_blood_pressure | Hypertension warning |
| warning_diabetes | Diabetes warning |
| warning_pregnancy | Pregnancy warning |
| warning_lactation | Breastfeeding warning |
| warning_kidney | Kidney disease warning |
| warning_liver | Liver disease warning |
| warning_heart | Heart disease warning |
| warnings_summary | Arabic warning summary |
| warnings_summary_en | English warning summary |

---

## Safety Warning Flags

The warning fields are automatically generated from ingredient-level FDA safety information.

### Values

- `1` → Warning or caution detected
- `0` → No warning detected

### Available Warning Categories

- High Blood Pressure
- Diabetes
- Pregnancy
- Lactation / Breastfeeding
- Kidney Disease
- Liver Disease
- Heart Disease

---

## Sample Record

```json
{
  "id": 1,
  "name": "1 2 3 (one two three) syrup 120 ml",
  "arabic": "ون تو ثري شراب 120 مل",
  "active": "Chlorpheniramine+paracetamol+pseudoephedrine",
  "company": "Hikma",
  "price": "40.00.",
  "uses_summary": "تخفيف أعراض نزلات البرد والإنفلونزا...",
  "uses_summary_en": "temporarily relieves nasal congestion...",
  "warning_high_blood_pressure": 1,
  "warning_diabetes": 1,
  "warning_pregnancy": 1
}
```

---

## Loading Examples

### Python (CSV)

```python
import csv

with open("data/eg_drugs.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        print(row["name"], row["price"])
        break
```

### Python (JSON)

```python
import json

with open("data/eg_drugs.json", encoding="utf-8") as f:
    drugs = json.load(f)

print(len(drugs))
```

### Pandas

```python
import pandas as pd

df = pd.read_csv("data/eg_drugs.csv")

print(df.head())
```

---

## Query Examples

### Find Drugs With Pregnancy Warnings

```python
pregnancy_drugs = df[df["warning_pregnancy"] == 1]
```

### Find Drugs Without Diabetes Warnings

```python
safe_for_diabetes = df[df["warning_diabetes"] == 0]
```

### Search By Active Ingredient

```python
results = df[df["active"].str.contains("paracetamol", case=False)]
```

### SQL Example

```sql
SELECT *
FROM drugs
WHERE warning_pregnancy = 1;
```

---

## Potential Use Cases

- Pharmacy Management Systems
- Drug Search Engines
- Healthcare Applications
- Clinical Decision Support Tools
- AI Medical Assistants
- Drug Recommendation Systems
- Pharmaceutical Market Analysis
- Academic Research
- Arabic NLP & Healthcare AI

---

## License

This dataset is available for:

- Personal Projects
- Educational Use
- Research Purposes
- Non-Commercial Applications

Commercial usage may require separate permission from the dataset owner.

---

## Citation

If you use this dataset in research or academic work, please cite:

```text
Egyptian Drug Database (eg_drugs)
Mahmoud Mohamed
Version: June 2026
26,562 FDA-Enriched Egyptian Pharmaceutical Products
```

---

## Contact

For questions, issues, or contributions:

- GitHub Issues (Preferred)
- Email: mahmoudfalous@gmail.com

---

**Version:** June 2026  
**Records:** 26,562  
**Language:** Arabic + English  
**Coverage:** Egyptian Pharmaceutical Products
