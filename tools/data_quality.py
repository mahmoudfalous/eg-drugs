"""
أدوات جودة البيانات لقاعدة بيانات الأدوية المصرية (eg-drugs).

الفحوصات المضمنة:
1. السجلات الناقصة الحقول الأساسية (name, arabic, active, price)
2. السجلات المكررة (حسب الاسم العربي أو الباركود)
3. اختلافات الأسعار (price vs oldprice) بنسب كبيرة
4. صحة الباركود (GS1 / EAN-13)
5. قيم غير صالحة في حقل barcode_valid

يخرج تقرير بصيغة JSON إلى stdout أو ملف مخرج.

تشغيل:
    python tools/data_quality.py --db data/eg_drugs.sqlite --report report.json
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

# استيراد دالة التحقق من الباركود من الملف المجاور
sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_barcodes import validate_barcode_any  # noqa: E402

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "eg_drugs.sqlite"

REQUIRED_FIELDS = ["name", "arabic", "active", "price"]


def connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def check_missing_fields(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    """السجلات التي تفتقر إلى أحد الحقول الأساسية."""
    issues: List[Dict[str, Any]] = []
    for field in REQUIRED_FIELDS:
        cur = conn.execute(
            f"SELECT id, name, arabic FROM eg_drugs WHERE {field} IS NULL OR {field} = ''"
        )
        for row in cur.fetchall():
            issues.append(
                {
                    "type": "missing_field",
                    "field": field,
                    "id": row["id"],
                    "name": row["name"],
                    "arabic": row["arabic"],
                    "severity": "high",
                }
            )
    return issues


def check_duplicates(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    """السجلات المكررة حسب الاسم العربي أو الباركود."""
    issues: List[Dict[str, Any]] = []

    # مكررات الاسم العربي
    cur = conn.execute(
        """
        SELECT arabic, COUNT(*) as c, GROUP_CONCAT(id) as ids
        FROM eg_drugs
        WHERE arabic IS NOT NULL AND arabic != ''
        GROUP BY arabic
        HAVING c > 1
        ORDER BY c DESC
        LIMIT 50
        """
    )
    for row in cur.fetchall():
        ids = [int(x) for x in row["ids"].split(",")]
        issues.append(
            {
                "type": "duplicate_arabic",
                "arabic": row["arabic"],
                "count": row["c"],
                "ids": ids,
                "severity": "medium",
            }
        )

    # مكررات الباركود (فقط الباركود غير الفارغ والصحيح الشكل)
    cur = conn.execute(
        """
        SELECT barcode, COUNT(*) as c, GROUP_CONCAT(id) as ids
        FROM eg_drugs
        WHERE barcode IS NOT NULL AND barcode != '' AND barcode != '0'
        GROUP BY barcode
        HAVING c > 1
        ORDER BY c DESC
        LIMIT 50
        """
    )
    for row in cur.fetchall():
        ids = [int(x) for x in row["ids"].split(",")]
        issues.append(
            {
                "type": "duplicate_barcode",
                "barcode": row["barcode"],
                "count": row["c"],
                "ids": ids,
                "severity": "medium",
            }
        )

    return issues


def check_price_anomalies(conn: sqlite3.Connection, threshold_pct: float = 50.0) -> List[Dict[str, Any]]:
    """اكتشاف اختلافات كبيرة في الأسعار بين price و oldprice."""
    issues: List[Dict[str, Any]] = []
    cur = conn.execute(
        """
        SELECT id, name, arabic, price, oldprice
        FROM eg_drugs
        WHERE price IS NOT NULL AND price != ''
          AND oldprice IS NOT NULL AND oldprice != ''
        """
    )
    for row in cur.fetchall():
        try:
            price = float(row["price"])
            oldprice = float(row["oldprice"])
        except (ValueError, TypeError):
            continue
        if oldprice <= 0:
            continue
        change_pct = abs(price - oldprice) / oldprice * 100
        if change_pct >= threshold_pct:
            issues.append(
                {
                    "type": "price_anomaly",
                    "id": row["id"],
                    "name": row["name"],
                    "arabic": row["arabic"],
                    "price": price,
                    "oldprice": oldprice,
                    "change_pct": round(change_pct, 2),
                    "severity": "high" if change_pct >= 100 else "medium",
                }
            )
    return issues


def check_barcodes(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    """التحقق من صحة الباركود وحقل barcode_valid."""
    issues: List[Dict[str, Any]] = []
    cur = conn.execute(
        "SELECT id, name, arabic, barcode, barcode_valid FROM eg_drugs WHERE barcode IS NOT NULL AND barcode != ''"
    )
    for row in cur.fetchall():
        barcode = row["barcode"] or ""
        valid_flag = row["barcode_valid"]

        is_valid, message = validate_barcode_any(barcode)

        # إذا كان الباركود طول 13 وغير صالح GS1
        if len(barcode) == 13 and not is_valid:
            issues.append(
                {
                    "type": "invalid_barcode",
                    "id": row["id"],
                    "name": row["name"],
                    "arabic": row["arabic"],
                    "barcode": barcode,
                    "reason": message,
                    "severity": "medium",
                }
            )

        # تناقض بين حقل barcode_valid والحقيقة
        if len(barcode) == 13:
            expected_valid = "1" if is_valid else "0"
            if valid_flag != expected_valid:
                issues.append(
                    {
                        "type": "barcode_valid_mismatch",
                        "id": row["id"],
                        "name": row["name"],
                        "arabic": row["arabic"],
                        "barcode": barcode,
                        "field_value": valid_flag,
                        "expected": expected_valid,
                        "severity": "low",
                    }
                )

    return issues


def run_all_checks(db_path: Path, threshold_pct: float = 50.0) -> Dict[str, Any]:
    """تشغيل جميع فحوصات الجودة وإرجاع التقرير."""
    conn = connect(db_path)
    try:
        total = conn.execute("SELECT COUNT(*) FROM eg_drugs").fetchone()[0]

        report: Dict[str, Any] = {
            "database": str(db_path),
            "total_records": total,
            "checks": {},
        }

        report["checks"]["missing_fields"] = check_missing_fields(conn)
        report["checks"]["duplicates"] = check_duplicates(conn)
        report["checks"]["price_anomalies"] = check_price_anomalies(
            conn, threshold_pct=threshold_pct
        )
        report["checks"]["barcodes"] = check_barcodes(conn)

        # ملخص
        summary = {
            "missing_fields_count": len(report["checks"]["missing_fields"]),
            "duplicate_groups_count": len(report["checks"]["duplicates"]),
            "price_anomalies_count": len(report["checks"]["price_anomalies"]),
            "barcode_issues_count": len(report["checks"]["barcodes"]),
        }
        summary["total_issues"] = sum(summary.values())
        report["summary"] = summary
        return report
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="فحص جودة بيانات eg-drugs (البطاقات، المكررات، الأسعار، الحقول الناقصة)"
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB_PATH,
        help="مسار ملف SQLite (الافتراضي: data/eg_drugs.sqlite)",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help="مسار ملف تقرير JSON للمخرج (الافتراضي: stdout)",
    )
    parser.add_argument(
        "--price-threshold",
        type=float,
        default=50.0,
        help="عتبة نسبة التغيير في السعر للإبلاغ عنها (الافتراضي: 50%)",
    )
    args = parser.parse_args()

    if not args.db.exists():
        print(f"خطأ: ملف قاعدة البيانات غير موجود: {args.db}", file=sys.stderr)
        sys.exit(1)

    report = run_all_checks(args.db, threshold_pct=args.price_threshold)

    output = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        args.report.write_text(output, encoding="utf-8")
        print(f"تم حفظ التقرير في: {args.report}")
    else:
        print(output)


if __name__ == "__main__":
    main()
