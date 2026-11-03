"""
العميل الرئيسي لمكتبة eg-drugs (Python SDK).

يدعم العمل بطريقتين:
1. محليًا: قراءة من ملف SQLite أو JSON موجود في المستودع.
2. عن بعد: استدعاء واجهة برمجة التطبيقات (REST API) عبر HTTP.
"""

from __future__ import annotations

import json
import sqlite3
import urllib.request
import urllib.parse
from pathlib import Path
from typing import List, Optional, Dict, Any, Union

from .models import Drug, Stats

DEFAULT_DB_PATH = (
    Path(__file__).resolve().parent.parent.parent.parent.parent / "data" / "eg_drugs.sqlite"
)
DEFAULT_JSON_PATH = (
    Path(__file__).resolve().parent.parent.parent.parent.parent / "data" / "eg_drugs.json"
)


class EgDrugsClient:
    """
    عميل للبحث في قاعدة بيانات الأدوية المصرية.

    매개변수:
        base_url: عنوان واجهة برمجة التطبيقات (اختياري). إذا لم يُعطى، تُستخدم الملفات المحلية.
        db_path: مسار ملف SQLite المحلي (اختياري).
        json_path: مسار ملف JSON المحلي (اختياري).
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        db_path: Optional[Union[str, Path]] = None,
        json_path: Optional[Union[str, Path]] = None,
    ):
        self.base_url = base_url.rstrip("/") if base_url else None
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.json_path = Path(json_path) if json_path else DEFAULT_JSON_PATH

    # ------------------------------------------------------------------
    # 내부 helper: استدعاء API عن بعد
    # ------------------------------------------------------------------
    def _fetch_json(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        if not self.base_url:
            raise RuntimeError("base_url غير محدد. يرجى تمريره عند إنشاء العميل أو استخدام الملفات المحلية.")
        url = self.base_url + path
        if params:
            url += "?" + urllib.parse.urlencode(params)
        with urllib.request.urlopen(url, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))

    # ------------------------------------------------------------------
    # innen helper: قراءة من الملفات المحلية
    # ------------------------------------------------------------------
    def _local_search(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0,
        fields: Optional[List[str]] = None,
    ) -> List[Drug]:
        """
        بحث محلي في ملف SQLite باستخدام LIKE على الحقول المحددة.
        """
        if fields is None:
            fields = ["name", "arabic", "active", "company"]

        if not self.db_path.exists():
            raise FileNotFoundError(f"ملف SQLite غير موجود: {self.db_path}")

        like = f"%{query}%"
        conditions = " OR ".join(f"{f} LIKE ?" for f in fields)
        params = [like] * len(fields) + [limit, offset]

        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            cur = conn.execute(
                f"""
                SELECT * FROM eg_drugs
                WHERE {conditions}
                ORDER BY id
                LIMIT ? OFFSET ?
                """,
                params,
            )
            rows = cur.fetchall()
            return [Drug.from_dict(dict(r)) for r in rows]
        finally:
            conn.close()

    def _local_get_by_id(self, drug_id: int) -> Optional[Drug]:
        if not self.db_path.exists():
            raise FileNotFoundError(f"ملف SQLite غير موجود: {self.db_path}")
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            cur = conn.execute("SELECT * FROM eg_drugs WHERE id = ?", (drug_id,))
            row = cur.fetchone()
            return Drug.from_dict(dict(row)) if row else None
        finally:
            conn.close()

    def _local_get_by_barcode(self, barcode: str) -> Optional[Drug]:
        if not self.db_path.exists():
            raise FileNotFoundError(f"ملف SQLite غير موجود: {self.db_path}")
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            cur = conn.execute("SELECT * FROM eg_drugs WHERE barcode = ?", (barcode,))
            row = cur.fetchone()
            return Drug.from_dict(dict(row)) if row else None
        finally:
            conn.close()

    def _local_get_generics(
        self,
        active: str,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Drug]:
        if not self.db_path.exists():
            raise FileNotFoundError(f"ملف SQLite غير موجود: {self.db_path}")
        like = f"%{active}%"
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
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
            return [Drug.from_dict(dict(r)) for r in rows]
        finally:
            conn.close()

    def _local_stats(self) -> Stats:
        if not self.db_path.exists():
            raise FileNotFoundError(f"ملف SQLite غير موجود: {self.db_path}")
        conn = sqlite3.connect(str(self.db_path))
        try:
            cur = conn.cursor()
            total = cur.execute("SELECT COUNT(*) FROM eg_drugs").fetchone()[0]
            companies = cur.execute(
                "SELECT COUNT(DISTINCT company) FROM eg_drugs WHERE company IS NOT NULL AND company != ''"
            ).fetchone()[0]
            categories = cur.execute(
                "SELECT COUNT(DISTINCT description) FROM eg_drugs WHERE description IS NOT NULL AND description != ''"
            ).fetchone()[0]
            actives = cur.execute(
                "SELECT COUNT(DISTINCT active) FROM eg_drugs WHERE active IS NOT NULL AND active != ''"
            ).fetchone()[0]
            valid_barcodes = cur.execute(
                "SELECT COUNT(*) FROM eg_drugs WHERE barcode_valid = '1'"
            ).fetchone()[0]
            price_changed = cur.execute(
                "SELECT COUNT(*) FROM eg_drugs WHERE price != oldprice AND oldprice IS NOT NULL AND oldprice != ''"
            ).fetchone()[0]
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

    # ------------------------------------------------------------------
    # واجهة عامة
    # ------------------------------------------------------------------
    def search(
        self,
        q: str,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Drug]:
        """
        بحث بالأسماء العربية أو الإنجليزية، المادة الفعالة، أو الشركة.
        """
        if self.base_url:
            data = self._fetch_json("/drugs/search", {"q": q, "limit": limit, "offset": offset})
            return [Drug.from_dict(item) for item in data]
        return self._local_search(q, limit=limit, offset=offset)

    def get_by_id(self, drug_id: int) -> Optional[Drug]:
        """جلب دواء بالمعرف الرقمي."""
        if self.base_url:
            data = self._fetch_json(f"/drugs/{drug_id}")
            return Drug.from_dict(data)
        return self._local_get_by_id(drug_id)

    def get_by_barcode(self, barcode: str) -> Optional[Drug]:
        """جلب دواء برقم الباركود."""
        if self.base_url:
            data = self._fetch_json(f"/drugs/barcode/{barcode}")
            return Drug.from_dict(data)
        return self._local_get_by_barcode(barcode)

    def get_generics(
        self,
        active: str,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Drug]:
        """إرجاع الأدوية التي تحتوي على نفس المادة الفعالة (بدائل/ج enerics)."""
        if self.base_url:
            data = self._fetch_json(
                "/drugs/generics/" + active,
                {"limit": limit, "offset": offset},
            )
            return [Drug.from_dict(item) for item in data]
        return self._local_get_generics(active, limit=limit, offset=offset)

    def stats(self) -> Stats:
        """إحصائيات قاعدة البيانات."""
        if self.base_url:
            data = self._fetch_json("/stats")
            return Stats.from_dict(data)
        return self._local_stats()


# ------------------------------------------------------------------
# دوال مساعدة للاستخدام السريع بدون إنشاء عميل
# ------------------------------------------------------------------
def _default_client() -> EgDrugsClient:
    return EgDrugsClient()


def search(q: str, limit: int = 20, offset: int = 0) -> List[Drug]:
    return _default_client().search(q, limit=limit, offset=offset)


def search_by_active(active: str, limit: int = 50, offset: int = 0) -> List[Drug]:
    return _default_client().get_generics(active, limit=limit, offset=offset)


def search_by_company(company: str, limit: int = 50, offset: int = 0) -> List[Drug]:
    # البحث عبر حقل الشركة باستخدام البحث العام
    return _default_client().search(company, limit=limit, offset=offset)


def get_by_id(drug_id: int) -> Optional[Drug]:
    return _default_client().get_by_id(drug_id)


def get_by_barcode(barcode: str) -> Optional[Drug]:
    return _default_client().get_by_barcode(barcode)


def get_generics(active: str, limit: int = 50, offset: int = 0) -> List[Drug]:
    return _default_client().get_generics(active, limit=limit, offset=offset)


def load_stats() -> Stats:
    return _default_client().stats()
