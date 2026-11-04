"""
Data quality tools for the Egyptian Drug Database (eg-drugs).

Included checks:
1. Records missing required fields (name, arabic, active, price)
2. Duplicate records (by Arabic name or barcode)
3. Large price differences (price vs oldprice)
4. Barcode validity (GS1 / EAN-13)
5. Invalid barcode_valid field values

Outputs a JSON report to stdout or an output file.

Usage:
    python tools/data_quality.py --db data/eg_drugs.sqlite --report report.json
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Import barcode validation function from the adjacent file
sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_barcodes import validate_barcode_any  # noqa: E402

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "eg_drugs.sqlite"

REQUIRED_FIELDS = ["name", "arabic", "active", "price"]


def connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def check_missing_fields(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    """Records missing one of the required fields."""
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
    """Duplicate records by Arabic name or barcode."""
    issues: List[Dict[str, Any]] = []

    # Duplicate Arabic names
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

    # Duplicate barcodes (non-empty, non-zero barcodes only)
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


def check_price_anomalies(
    conn: sqlite3.Connection, threshold_pct: float = 50.0
) -> List[Dict[str, Any]]:
    """Detect large price differences between price and oldprice."""
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
    """Validate barcodes and the barcode_valid field."""
    issues: List[Dict[str, Any]] = []
    cur = conn.execute(
        "SELECT id, name, arabic, barcode, barcode_valid FROM eg_drugs WHERE barcode IS NOT NULL AND barcode != ''"
    )
    for row in cur.fetchall():
        barcode = row["barcode"] or ""
        valid_flag = row["barcode_valid"]

        is_valid, message = validate_barcode_any(barcode)

        # If barcode is 13 digits and not valid GS1
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

        # Inconsistency between barcode_valid field and reality
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
    """Run all quality checks and return the report."""
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

        # Summary
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
        description="Check eg-drugs data quality (barcodes, duplicates, prices, missing fields)"
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB_PATH,
        help="Path to SQLite file (default: data/eg_drugs.sqlite)",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help="Path to output JSON report file (default: stdout)",
    )
    parser.add_argument(
        "--price-threshold",
        type=float,
        default=50.0,
        help="Price change percentage threshold for reporting (default: 50%)",
    )
    args = parser.parse_args()

    if not args.db.exists():
        print(f"Error: database file not found: {args.db}", file=sys.stderr)
        sys.exit(1)

    report = run_all_checks(args.db, threshold_pct=args.price_threshold)

    output = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        args.report.write_text(output, encoding="utf-8")
        print(f"Report saved to: {args.report}")
    else:
        print(output)


if __name__ == "__main__":
    main()
