/**
 * eg-drugs Node.js SDK
 * ====================
 * مكتبة Node.js للوصول إلى قاعدة بيانات الأدوية المصرية (eg-drugs).
 *
 * البحث بالأسماء العربية أو الإنجليزية، المادة الفعالة، الشركة، أو الباركود،
 * وإيجاد الأدوية البديلة (نفس المادة الفعالة).
 *
 * مثال سريع:
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
 * عميل eg-drugs لـ Node.js.
 * يدعم العمل محليًا (ملف SQLite أو JSON) أو عن بعد عبر واجهة برمجة التطبيقات.
 */
class EgDrugsClient {
  constructor({ baseUrl, dbPath, jsonPath } = {}) {
    this.baseUrl = baseUrl ? baseUrl.replace(/\/+$/, "") : null;
    this.dbPath = dbPath || DEFAULT_DB_PATH;
    this.jsonPath = jsonPath || DEFAULT_JSON_PATH;
    this._jsonCache = null;
  }

  /**
   * استدعاء واجهة API عن بعد وإرجاع JSON.
   * @private
   */
  async _fetchJson(apiPath, params = {}) {
    if (!this.baseUrl) {
      throw new Error(
        "baseUrl غير محدد. يرجى تمريره عند إنشاء العميل أو استخدام الملفات المحلية."
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
   * قراءة جميع السجلات من ملف JSON محلي (مع التخزين المؤقت).
   * @private
   */
  _loadJson() {
    if (this._jsonCache) return this._jsonCache;
    if (!fs.existsSync(this.jsonPath)) {
      throw new Error(`ملف JSON غير موجود: ${this.jsonPath}`);
    }
    this._jsonCache = JSON.parse(fs.readFileSync(this.jsonPath, "utf8"));
    return this._jsonCache;
  }

  /**
   * تشغيل استعلام sqlite3 عبر سطر الأوامر، مع fallback إلى JSON إذا لم يكن sqlite3 مثبتاً.
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
      // sqlite3 غير مثبت أو فشل -> fallback إلى JSON
      return null;
    }
  }

  /**
   * تحويل سجل إلى كائن موحد.
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
   * فلترة السجلات من JSON وفق كلمة بحث.
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
   * بحث بالأسماء العربية أو الإنجليزية، المادة الفعالة، أو الشركة.
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
   * جلب دواء بالمعرف الرقمي.
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
   * جلب دواء برقم الباركود.
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
   * إرجاع الأدوية التي تحتوي على نفس المادة الفعالة (بدائل/ج enerics).
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
   * إحصائيات قاعدة البيانات.
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
 * إنشاء عميل افتراضي يعمل مع الملفات المحلية في المستودع.
 */
function createClient(options = {}) {
  return new EgDrugsClient(options);
}

/**
 * دوال مساعدة للاستخدام السريع.
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
