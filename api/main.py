"""
eg-drugs REST API
=================
واجهة برمجة تطبيقات لقاعدة بيانات الأدوية المصرية (eg-drugs).
تمكنك من البحث عن الأدوية باسمها العربي أو الإنجليزي، المادة الفعالة، الشركة، أو الباركود،
وإيجاد الأدوية البديلة (نفس المادة الفعالة).

تشغيل محلي:
    pip install -r api/requirements.txt
    uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

توثيق تفاعلي: http://localhost:8000/docs
"""

import sqlite3
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "eg_drugs.sqlite"

app = FastAPI(
    title="eg-drugs API",
    description="REST API للبحث في قاعدة بيانات الأدوية المصرية (27,617+ دواء)",
    version="1.0.0",
    contact={"name": "Abduallah Jamal", "url": "https://github.com/abduallahJamal"},
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
)


class Drug(BaseModel):
    id: int
    name: str
    arabic: str
    active: Optional[str] = None
    company: Optional[str] = None
    price: Optional[str] = None
    oldprice: Optional[str] = None
    barcode: Optional[str] = None
    barcode_valid: Optional[str] = None
    slug: Optional[str] = None
    units: Optional[str] = None
    description: Optional[str] = None
    uses: Optional[str] = None


class Stats(BaseModel):
    total_drugs: int
    unique_companies: int
    unique_categories: int
    unique_active_ingredients: int
    valid_barcodes: int
    price_changed: int


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def row_to_dict(row: sqlite3.Row) -> dict:
    return {key: row[key] for key in row.keys()}


@app.get("/", tags=["General"])
def read_root():
    return {
        "message": "مرحباً بك في واجهة برمجة تطبيقات eg-drugs",
        "version": "1.0.0",
        "endpoints": {
            "search": "/drugs/search?q=كلمة",
            "by_id": "/drugs/{id}",
            "by_barcode": "/drugs/barcode/{barcode}",
            "generics": "/drugs/generics/{active_ingredient}",
            "categories": "/categories",
            "companies": "/companies",
            "stats": "/stats",
            "docs": "/docs",
        },
        "database": "eg_drugs.sqlite (27,617+ دواء)",
    }


@app.get("/drugs/search", response_model=List[Drug], tags=["Search"])
def search_drugs(
    q: str = Query(..., description="كلمة بحث (اسم إنجليزي، عربي، مادة فعالة، شركة)"),
    limit: int = Query(20, ge=1, le=100, description="عدد النتائج القصوى"),
    offset: int = Query(0, ge=0, description="تسجيلات للتخطي (للتصفح)"),
):
    conn = get_conn()
    try:
        like = f"%{q}%"
        cur = conn.execute(
            """
            SELECT * FROM eg_drugs
            WHERE name LIKE ? OR arabic LIKE ? OR active LIKE ? OR company LIKE ?
            ORDER BY id
            LIMIT ? OFFSET ?
            """,
            (like, like, like, like, limit, offset),
        )
        rows = cur.fetchall()
        return [row_to_dict(r) for r in rows]
    finally:
        conn.close()


@app.get("/drugs/{drug_id}", response_model=Drug, tags=["Search"])
def get_drug(drug_id: int):
    conn = get_conn()
    try:
        cur = conn.execute("SELECT * FROM eg_drugs WHERE id = ?", (drug_id,))
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="الدواء غير موجود")
        return row_to_dict(row)
    finally:
        conn.close()


@app.get("/drugs/barcode/{barcode}", response_model=Drug, tags=["Search"])
def get_drug_by_barcode(barcode: str):
    conn = get_conn()
    try:
        cur = conn.execute("SELECT * FROM eg_drugs WHERE barcode = ?", (barcode,))
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="الباركود غير موجود")
        return row_to_dict(row)
    finally:
        conn.close()


@app.get("/drugs/generics/{active}", response_model=List[Drug], tags=["Generics"])
def get_generics(
    active: str,
    limit: int = Query(50, ge=1, le=200, description="عدد النتائج القصوى"),
    offset: int = Query(0, ge=0, description="تسجيلات للتخطي (للتصفح)"),
):
    """
    إعادة الأدوية التي تحتوي على نفس المادة الفعالة (الأدوية البديلة/الج네ريك).
    """
    conn = get_conn()
    try:
        like = f"%{active}%"
        cur = conn.execute(
            """
            SELECT * FROM eg_drugs
            WHERE active LIKE ?
            ORDER BY id
            LIMIT ? OFFSET ?
            """,
            (like, limit, offset),
        )
        rows = cur.fetchall()
        return [row_to_dict(r) for r in rows]
    finally:
        conn.close()


@app.get("/categories", tags=["Reference"])
def list_categories(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    conn = get_conn()
    try:
        cur = conn.execute(
            """
            SELECT description AS category, COUNT(*) AS count
            FROM eg_drugs
            WHERE description IS NOT NULL AND description != ''
            GROUP BY description
            ORDER BY count DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        )
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


@app.get("/companies", tags=["Reference"])
def list_companies(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    conn = get_conn()
    try:
        cur = conn.execute(
            """
            SELECT company, COUNT(*) AS count
            FROM eg_drugs
            WHERE company IS NOT NULL AND company != ''
            GROUP BY company
            ORDER BY count DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        )
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


@app.get("/stats", response_model=Stats, tags=["Stats"])
def get_stats():
    conn = get_conn()
    try:
        cur = conn.execute("SELECT COUNT(*) FROM eg_drugs")
        total = cur.fetchone()[0]

        cur = conn.execute(
            "SELECT COUNT(DISTINCT company) FROM eg_drugs WHERE company IS NOT NULL AND company != ''"
        )
        companies = cur.fetchone()[0]

        cur = conn.execute(
            "SELECT COUNT(DISTINCT description) FROM eg_drugs WHERE description IS NOT NULL AND description != ''"
        )
        categories = cur.fetchone()[0]

        cur = conn.execute(
            "SELECT COUNT(DISTINCT active) FROM eg_drugs WHERE active IS NOT NULL AND active != ''"
        )
        actives = cur.fetchone()[0]

        cur = conn.execute(
            "SELECT COUNT(*) FROM eg_drugs WHERE barcode_valid = '1'"
        )
        valid_barcodes = cur.fetchone()[0]

        cur = conn.execute(
            "SELECT COUNT(*) FROM eg_drugs WHERE price != oldprice AND oldprice IS NOT NULL AND oldprice != ''"
        )
        price_changed = cur.fetchone()[0]

        return Stats(
            total_drugs=total,
            unique_companies=companies,
            unique_categories=categories,
            unique_active_ingredients=actives,
            valid_barcodes=valid_barcodes,
            price_changed=price_changed,
        )
    finally:
        conn.close()


@app.get("/health", tags=["General"])
def health():
    return {"status": "ok"}
