# Egyptian Drug Database (`eg_drugs`)

A clean, standardized, and continuously updated pharmaceutical database containing **27,617+ drugs marketed in Egypt**, including active ingredients, commercial names in Arabic and English, current and historical prices, manufacturers, barcodes, and medical categories.

All files are located in the `data/` directory and available in **CSV**, **JSON**, **SQLite**, and **SQL dump** formats.

---

## Files Overview

| File | Format | Size | Description |
| :--- | :--- | :--- | :--- |
| **`data/eg_drugs.csv`** | CSV (UTF-8) | ~8.1 MB | Comma-separated tabular data for Pandas, Excel, or ETL pipelines. |
| **`data/eg_drugs.json`** | JSON Array | ~16 MB | Array of drug objects for web, mobile, and API runtimes. |
| **`data/eg_drugs.sqlite`** | SQLite DB | ~13 MB | Relational SQLite database with built-in indexes on `name`, `arabic`, `active`, and `barcode`. |
| **`data/eg_drugs.sql`** | SQL Dump | ~9.7 MB | Standard SQL DDL & `INSERT` statements compatible with SQLite, PostgreSQL, and MySQL. |

---

## Schema Definition

All formats share the exact same schema structure:

| Field Name | Type (SQL / CSV) | Type (JSON) | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER PRIMARY KEY | Integer | Unique identifier for each drug record. |
| `name` | TEXT | String | Commercial/Brand name of the drug in English. |
| `arabic` | TEXT | String | Commercial/Brand name of the drug in Arabic. |
| `active` | TEXT | String | Active pharmaceutical ingredients/compounds. |
| `company` | TEXT | String | Manufacturing or distributing pharmaceutical company. |
| `price` | TEXT | String | Current retail price in EGP. |
| `oldprice` | TEXT | String | Previous retail price in EGP (for tracking price updates). |
| `barcode` | TEXT | String | Barcode number (EAN/GTIN). |
| `barcode_valid` | TEXT (0/1) | String ("0"/"1") | GS1 checksum validation flag (`1` = valid GTIN, `0` = invalid/absent). |
| `slug` | TEXT | String | URL-friendly slug identifier. |
| `units` | TEXT | String | Number of packaging units / pack size. |
| `description` | TEXT | String | Category classification (e.g., `cold products`, `antineoplastic`). |
| `uses` | TEXT | String | Indications and therapeutic usage in Arabic. |

---

## Data Samples

### JSON Record (`data/eg_drugs.json`)

```json
{
  "id": 1,
  "name": "1 2 3 (one two three) syrup 120 ml",
  "arabic": "ون تو ثري شراب 120 مل",
  "active": "chlorpheniramine+paracetamol+pseudoephedrine",
  "company": "hikma pharma",
  "price": "40",
  "oldprice": "32",
  "barcode": "6221000003295",
  "slug": "1-2-3--one-two-three--syrup-120-ml",
  "units": "1",
  "description": "cold products",
  "uses": "تخفيف أعراض نزلات البرد والإنفلونزا مثل الصداع وارتفاع درجة الحرارة...",
  "barcode_valid": "1"
}
```

---

## Loading and Usage Guidelines

### 1. SQLite Database (`data/eg_drugs.sqlite`)

The SQLite database includes pre-built indexes for instant lookups by English name, Arabic name, active ingredient, or barcode:

```python
import sqlite3

conn = sqlite3.connect("data/eg_drugs.sqlite")
cursor = conn.cursor()

# Search by active ingredient
cursor.execute(
    "SELECT name, arabic, price, company FROM eg_drugs WHERE active LIKE ? LIMIT 5",
    ("%paracetamol%",),
)
for row in cursor.fetchall():
    print(row)
```

Command line quick query:
```bash
sqlite3 data/eg_drugs.sqlite "SELECT name, price FROM eg_drugs WHERE name LIKE '%concor%' LIMIT 5;"
```

---

### 2. Standard SQL Dump (`data/eg_drugs.sql`)

Import directly into PostgreSQL, MySQL, or SQLite:

```bash
# SQLite
sqlite3 my_database.sqlite < data/eg_drugs.sql

# PostgreSQL
psql -d my_database -f data/eg_drugs.sql

# MySQL
mysql -u root -p my_database < data/eg_drugs.sql
```

---

### 3. Python (CSV / Pandas)

```python
import pandas as pd

df = pd.read_csv("data/eg_drugs.csv")
print(f"Total drugs: {len(df)}")

# Filter drugs by company
hikma_drugs = df[df["company"].str.contains("hikma", case=False, na=False)]
print(hikma_drugs[["name", "price", "active"]].head())
```

---

### 4. JavaScript / Node.js (JSON)

```javascript
const fs = require('fs');

const drugs = JSON.parse(fs.readFileSync('data/eg_drugs.json', 'utf8'));
console.log(`Loaded ${drugs.length} drugs.`);

const aspirin = drugs.filter(d => d.name.toLowerCase().includes('aspirin'));
console.log(`Found ${aspirin.length} aspirin products.`);
```

---

## License & Contact

* **Usage**: You are free to use this database in any unpaid (non-commercial) projects and research.
* **Updates**: Updated automatically via daily sync pipeline from [dwa-scrapping](https://github.com/mahmoudfalous/dwa-scrapping).
* **Contact**: [mahmoudfalous@gmail.com](mailto:mahmoudfalous@gmail.com).
