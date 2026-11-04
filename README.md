# Egyptian Drug Database (`eg_drugs`)

A clean, standardized pharmaceutical database containing **27,617+ drugs marketed in Egypt**, including active ingredients, commercial names in Arabic and English, current and previous retail prices, manufacturers, barcodes, and medical categories.

Available in **CSV**, **JSON**, **SQLite**, and **SQL dump** formats under `data/`.

---

## 🚀 Added in this fork

| Component | Path | Description |
|-----------|------|-------------|
| REST API | `api/main.py` | FastAPI search API for drugs, barcodes, and generics |
| Web UI | `web/index.html` | Arabic search interface |
| Python SDK | `sdk/python/eg_drugs` | Python library for programmatic access |
| Node.js SDK | `sdk/node/eg-drugs` | Node.js library for programmatic access |
| Data quality tools | `tools/` | Barcode validation, duplicate detection, price anomaly checks |
| Price tracking | `tools/price_tracker.py` | Compare drug prices between data versions |
| Export formats | `tools/export_formats.py` | Export to Excel (.xlsx) and Parquet (.parquet) |
| CI | `.github/workflows/` | GitHub Actions for build/tests/data quality |

---

## 🔌 REST API

```bash
pip install -r api/requirements.txt
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Interactive docs: `http://localhost:8000/docs`

Key endpoints:
- `GET /drugs/search?q=keyword` — search drugs
- `GET /drugs/{id}` — get drug by ID
- `GET /drugs/barcode/{barcode}` — get drug by barcode
- `GET /drugs/generics/{active}` — generic alternatives (same active ingredient)
- `GET /stats` — database statistics
- `GET /health` — health check

---

## 📦 SDKs

**Python:**
```bash
pip install -e sdk/python/eg_drugs
```
```python
from eg_drugs import search
results = search("panadol", limit=5)
```

**Node.js:**
```bash
cd sdk/node/eg-drugs && npm install
```
```js
const { search } = require('eg-drugs');
const results = await search('panadol', { limit: 5 });
```

---

## 🛠️ Tools

- `tools/data_quality.py` — data quality report (missing fields, duplicates, price anomalies, barcode validation)
- `tools/price_tracker.py` — track price changes between data versions
- `tools/export_formats.py` — export to Excel/Parquet

---

## 📄 License

Code: MIT License (`LICENSE-MIT`)
Data: CC-BY-4.0 (`LICENSE-DATA`)
