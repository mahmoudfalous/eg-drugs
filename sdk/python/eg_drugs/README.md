# eg-drugs Python SDK

Python library for accessing the Egyptian Drug Database (**eg-drugs**) — 27,617+ drugs.

## Install

```bash
pip install -e sdk/python/eg_drugs
```

Or directly from GitHub:

```bash
pip install git+https://github.com/abduallahJamal/eg-drugs.git#subdirectory=sdk/python/eg_drugs
```

## Quick start

```python
from eg_drugs import search, get_by_id, get_by_barcode, get_generics, load_stats

# Search by name (English or Arabic)
results = search("panadol", limit=5)
for drug in results:
    print(drug.arabic, "-", drug.price)

# Get drug by ID
drug = get_by_id(1)
print(drug.arabic, drug.active)

# Get drug by barcode
drug = get_by_barcode("6221000003295")
print(drug.name, drug.company)

# Generic alternatives (same active ingredient)
generics = get_generics("paracetamol", limit=10)
for g in generics:
    print(g.arabic, g.price)

# Database statistics
stats = load_stats()
print(f"Total drugs: {stats.total_drugs:,}")
print(f"Companies: {stats.unique_companies}")
print(f"Active ingredients: {stats.unique_active_ingredients}")
```

## Remote API

If you have an API server running at a given URL:

```python
from eg_drugs import EgDrugsClient

client = EgDrugsClient(base_url="https://api.example.com")
results = client.search("panadol", limit=10)
```

## Local files

By default, the library searches `data/eg_drugs.sqlite` in the repository.
You can pass a custom path:

```python
from eg_drugs import EgDrugsClient

client = EgDrugsClient(db_path="/path/to/eg_drugs.sqlite")
results = client.search("panadol")
```

## License

MIT License — see `LICENSE-MIT` in the repository root.
