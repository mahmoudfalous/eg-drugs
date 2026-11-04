# eg-drugs Node.js SDK

Node.js library for accessing the Egyptian Drug Database (**eg-drugs**) — 27,617+ drugs.

## Install

```bash
npm install
```
(inside the `sdk/node/eg-drugs` folder)

Or directly from GitHub:

```bash
npm install git+https://github.com/abduallahJamal/eg-drugs.git#subdirectory=sdk/node/eg-drugs
```

## Quick start

```js
const { search, getById, getByBarcode, getGenerics, loadStats } = require('eg-drugs');

// Search by name (English or Arabic)
const results = await search('panadol', { limit: 5 });
for (const drug of results) {
  console.log(drug.arabic, '-', drug.price);
}

// Get drug by ID
const drug = await getById(1);
console.log(drug.arabic, drug.active);

// Get drug by barcode
const drug2 = await getByBarcode('6221000003295');
console.log(drug2.name, drug2.company);

// Generic alternatives (same active ingredient)
const generics = await getGenerics('paracetamol', { limit: 10 });
for (const g of generics) {
  console.log(g.arabic, g.price);
}

// Database statistics
const stats = await loadStats();
console.log(`Total drugs: ${stats.totalDrugs.toLocaleString()}`);
console.log(`Companies: ${stats.uniqueCompanies}`);
console.log(`Active ingredients: ${stats.uniqueActiveIngredients}`);
```

## Remote API

```js
const { EgDrugsClient } = require('eg-drugs');

const client = new EgDrugsClient({ baseUrl: 'https://api.example.com' });
const results = await client.search('panadol', { limit: 10 });
```

## Local files

By default, the library searches `data/eg_drugs.sqlite` in the repository.
You can pass a custom path:

```js
const client = new EgDrugsClient({ dbPath: '/path/to/eg_drugs.sqlite' });
const results = await client.search('panadol');
```

## Requirements

- Node.js >= 18
- `sqlite3` CLI installed on the system (for fast local operation).
  If not installed, the library falls back to reading the JSON file.

## License

MIT License — see `LICENSE-MIT` in the repository root.
