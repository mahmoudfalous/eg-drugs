/**
 * eg-drugs Node.js SDK
 * ====================
 * Node.js library for accessing the Egyptian Drug Database (eg-drugs).
 *
 * Search drugs by name (Arabic/English), active ingredient, company, or barcode,
 * and find generic alternatives (same active ingredient).
 *
 * Quick example:
 *   const { search, getById, getByBarcode, getGenerics, loadStats } = require('eg-drugs');
 *
 *   const results = await search('panadol', { limit: 5 });
 *   for (const drug of results) {
 *     console.log(drug.arabic, drug.price);
 *   }
 */

const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

const DEFAULT_DB_PATH = path.resolve(
  __dirname,
  "../../../data/eg_drugs.sqlite"
);
const DEFAULT_JSON_PATH = path.resolve(
  __dirname,
  "../../../data/eg_drugs.json"
);

/**
 * eg-drugs client for Node.js.
 * Supports local operation (SQLite or JSON file) or remote API access.
 */
class EgDrugsClient {
  constructor({ baseUrl, dbPath, jsonPath } = {}) {
    this.baseUrl = baseUrl ? baseUrl.replace(/\/+$/, "") : null;
    this.dbPath = dbPath || DEFAULT_DB_PATH;
    this.jsonPath = jsonPath || DEFAULT_JSON_PATH;
    this._jsonCache = null;
  }

  /**
   * Call remote API and return JSON.
   * @private
   */
  async _fetchJson(apiPath, params = {}) {
    if (!this.baseUrl) {
      throw new Error(
        "baseUrl is not set. Pass it when creating the client or use local files."
      );
    }
    const qs = new URLSearchParams(params).toString();
    const url = `${this.baseUrl}${apiPath}${qs ? "?" + qs : ""}`;
    const resp = await fetch(url);
    if (!resp.ok) {
      throw new Error(`API error ${resp.status}: ${await resp.text()}`);
    }
    return resp.json();
  }

  /**
   * Load all records from a local JSON file (with caching).
   * @private
   */
  _loadJson() {
    if (this._jsonCache) return this._jsonCache;
    if (!fs.existsSync(this.jsonPath)) {
      throw new Error(`JSON file not found: ${this.jsonPath}`);
    }
    this._jsonCache = JSON.parse(fs.readFileSync(this.jsonPath, "utf8"));
    return this._jsonCache;
  }

  /**
   * Run a sqlite3 query via CLI, with fallback to JSON if sqlite3 is not installed.
   * @private
   */
  _runSqlite(sql) {
    try {
      const out = execSync(`sqlite3 -json "${this.dbPath}" ${JSON.stringify(sql)}`, {
        encoding: "utf8",
        maxBuffer: 100 * 1024 * 1024,
      });
      return JSON.parse(out);
    } catch (e) {
      // sqlite3 not installed or failed -> fallback to JSON
      return null;
    }
  }

  /**
   * Normalize a row into a consistent object.
   * @private
   */
  _normalizeRow(row) {
    return {
      id: Number(row.id),
      name: row.name || "",
      arabic: row.arabic || "",
      active: row.active || null,
      company: row.company || null,
      price: row.price || null,
      oldprice: row.oldprice || null,
      barcode: row.barcode || null,
      barcodeValid: row.barcode_valid || null,
      slug: row.slug || null,
      units: row.units || null,
      description: row.description || null,
      uses: row.uses || null,
    };
  }

  /**
   * Filter records from JSON by search keyword.
   * @private
   */
  _filterJson(query, { limit, offset } = {}) {
    const data = this._loadJson();
    const q = query.toLowerCase();
    const matches = data.filter(
      d =>
        (d.name && d.name.toLowerCase().includes(q)) ||
        (d.arabic && d.arabic.includes(q)) ||
        (d.active && d.active.toLowerCase().includes(q)) ||
        (d.company && d.company.toLowerCase().includes(q))
    );
    const sliced = matches.slice(offset || 0, (offset || 0) + (limit || matches.length));
    return sliced.map(d => this._normalizeRow(d));
  }

  /**
   * Search by name (Arabic/English), active ingredient, or company.
   */
  async search(q, { limit = 20, offset = 0 } = {}) {
    if (this.baseUrl) {
      const data = await this._fetchJson("/drugs/search", { q, limit, offset });
      return data.map(d => this._normalizeRow(d));
    }
    const sqliteRows = this._runSqlite(
      `SELECT * FROM eg_drugs WHERE name LIKE '%${q}%' OR arabic LIKE '%${q}%' OR active LIKE '%${q}%' OR company LIKE '%${q}%' ORDER BY id LIMIT ${Number(limit)} OFFSET ${Number(offset)};`
    );
    if (sqliteRows) return sqliteRows.map(r => this._normalizeRow(r));
    return this._filterJson(q, { limit, offset });
  }

  /**
   * Get a drug by its numeric ID.
   */
  async getById(id) {
    const numericId = Number(id);
    if (this.baseUrl) {
      const data = await this._fetchJson(`/drugs/${numericId}`);
      return this._normalizeRow(data);
    }
    const sqliteRows = this._runSqlite(
      `SELECT * FROM eg_drugs WHERE id = ${numericId};`
    );
    if (sqliteRows && sqliteRows.length) return this._normalizeRow(sqliteRows[0]);

    // fallback JSON
    const data = this._loadJson();
    const found = data.find(d => Number(d.id) === numericId);
    return found ? this._normalizeRow(found) : null;
  }

  /**
   * Get a drug by its barcode number.
   */
  async getByBarcode(barcode) {
    if (this.baseUrl) {
      const data = await this._fetchJson(`/drugs/barcode/${barcode}`);
      return this._normalizeRow(data);
    }
    const sqliteRows = this._runSqlite(
      `SELECT * FROM eg_drugs WHERE barcode = '${barcode}';`
    );
    if (sqliteRows && sqliteRows.length) return this._normalizeRow(sqliteRows[0]);

    // fallback JSON
    const data = this._loadJson();
    const found = data.find(d => d.barcode === barcode);
    return found ? this._normalizeRow(found) : null;
  }

  /**
   * Return drugs containing the same active ingredient (generic alternatives).
   */
  async getGenerics(active, { limit = 50, offset = 0 } = {}) {
    if (this.baseUrl) {
      const data = await this._fetchJson("/drugs/generics/" + active, {
        limit,
        offset,
      });
      return data.map(d => this._normalizeRow(d));
    }
    const sqliteRows = this._runSqlite(
      `SELECT * FROM eg_drugs WHERE active LIKE '%${active}%' ORDER BY id LIMIT ${Number(limit)} OFFSET ${Number(offset)};`
    );
    if (sqliteRows) return sqliteRows.map(r => this._normalizeRow(r));

    // fallback JSON
    const data = this._loadJson();
    const a = active.toLowerCase();
    const matches = data.filter(d => d.active && d.active.toLowerCase().includes(a));
    const sliced = matches.slice(offset || 0, (offset || 0) + (limit || matches.length));
    return sliced.map(d => this._normalizeRow(d));
  }

  /**
   * Database statistics.
   */
  async loadStats() {
    if (this.baseUrl) {
      return this._fetchJson("/stats");
    }
    const data = this._loadJson();
    const companies = new Set(data.filter(d => d.company).map(d => d.company)).size;
    const categories = new Set(data.filter(d => d.description).map(d => d.description)).size;
    const actives = new Set(data.filter(d => d.active).map(d => d.active)).size;
    const validBarcodes = data.filter(d => d.barcode_valid === "1").length;
    const priceChanged = data.filter(
      d => d.price && d.oldprice && d.price !== d.oldprice
    ).length;
    return {
      totalDrugs: data.length,
      uniqueCompanies: companies,
      uniqueCategories: categories,
      uniqueActiveIngredients: actives,
      validBarcodes,
      priceChanged,
    };
  }
}

/**
 * Create a default client that works with local files in the repository.
 */
function createClient(options = {}) {
  return new EgDrugsClient(options);
}

/**
 * Helper functions for quick use.
 */
async function search(q, options = {}) {
  return createClient().search(q, options);
}
async function getById(id) {
  return createClient().getById(id);
}
async function getByBarcode(barcode) {
  return createClient().getByBarcode(barcode);
}
async function getGenerics(active, options = {}) {
  return createClient().getGenerics(active, options);
}
async function loadStats() {
  return createClient().loadStats();
}

module.exports = {
  EgDrugsClient,
  createClient,
  search,
  getById,
  getByBarcode,
  getGenerics,
  loadStats,
};
