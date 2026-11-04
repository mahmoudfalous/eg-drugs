"""
eg-drugs REST API
=================
REST API for the Egyptian Drug Database (eg-drugs).
Search drugs by name (Arabic/English), active ingredient, company, or barcode,
and find generic alternatives (same active ingredient).

Local run:
    pip install -r api/requirements.txt
    uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

Interactive docs: http://localhost:8000/docs
"""

import json
import sqlite3
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "eg_drugs.sqlite"
PRICE_CHANGES_PATH = Path(__file__).resolve().parent.parent / "data" / "price_changes.json"
PRICE_CHANGES_SUMMARY_PATH = Path(__file__).resolve().parent.parent / "data" / "price_changes_summary.json"

app = FastAPI(
    title="eg-drugs API",
    description="REST API for the Egyptian Drug Database (27,617+ drugs)",
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
        "message": "Welcome to eg-drugs API",
        "version": "1.0.0",
        "endpoints": {
            "search": "/drugs/search?q=keyword",
            "by_id": "/drugs/{id}",
            "by_barcode": "/drugs/barcode/{barcode}",
            "generics": "/drugs/generics/{active_ingredient}",
            "categories": "/categories",
            "companies": "/companies",
            "stats": "/stats",
            "price_changes": "/price-changes",
            "price_changes_summary": "/price-changes/summary",
            "docs": "/docs",
        },
        "database": "eg_drugs.sqlite (27,617+ drugs)",
    }


@app.get("/drugs/search", response_model=List[Drug], tags=["Search"])
def search_drugs(
    q: str = Query(..., description="Search keyword (name in English/Arabic, active ingredient, company)"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Records to skip (pagination)"),
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
            raise HTTPException(status_code=404, detail="Drug not found")
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
            raise HTTPException(status_code=404, detail="Barcode not found")
        return row_to_dict(row)
    finally:
        conn.close()


@app.get("/drugs/generics/{active}", response_model=List[Drug], tags=["Generics"])
def get_generics(
    active: str,
    limit: int = Query(50, ge=1, le=200, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Records to skip (pagination)"),
):
    """
    Return drugs containing the same active ingredient (generic alternatives).
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


@app.get("/price-changes", tags=["Stats"])
def get_price_changes():
    """Return the list of price changes detected by tools/price_tracker.py."""
    if not PRICE_CHANGES_PATH.exists():
        return {
            "message": "No price change data available. Run tools/price_tracker.py first.",
            "changes": [],
        }
    with open(PRICE_CHANGES_PATH, encoding="utf-8") as f:
        changes = json.load(f)
    return {"changes": changes, "count": len(changes)}


@app.get("/price-changes/summary", tags=["Stats"])
def get_price_changes_summary():
    """Return summary statistics for price changes."""
    if not PRICE_CHANGES_SUMMARY_PATH.exists():
        return {
            "message": "No price change summary available. Run tools/price_tracker.py first.",
            "summary": {},
        }
    with open(PRICE_CHANGES_SUMMARY_PATH, encoding="utf-8") as f:
        summary = json.load(f)
    return summary


@app.get("/health", tags=["General"])
def health():
    return {"status": "ok"}
