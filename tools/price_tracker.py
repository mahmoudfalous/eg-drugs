"""
تتبع تغييرات الأسعار في قاعدة بيانات الأدوية المصرية.

يقارن بين إصدارين من بيانات الأدوية (الحالي والسابق) وينتج تقريراً
بجميع الأدوية التي تغيرت أسعارها، مع نسبة التغيير والاتجاه (زيادة/نقصان).

المخرجات:
- data/price_changes.json: قائمة بجميع الأدوية التي تغيرت أسعارها
- data/price_changes_summary.json: إحصائيات مجمعة

تشغيل:
    python tools/price_tracker.py --current data/eg_drugs.json --previous data/eg_drugs_previous.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_CURRENT = Path(__file__).resolve().parent.parent / "data" / "eg_drugs.json"
DEFAULT_OUTPUT = Path(__file__).resolve().parent.parent / "data" / "price_changes.json"
DEFAULT_SUMMARY = (
    Path(__file__).resolve().parent.parent / "data" / "price_changes_summary.json"
)


def load_json(path: Path) -> List[Dict[str, Any]]:
    with open(path, encoding="utf-8-sig") as f:
        return json.load(f)


def index_by_id(records: List[Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
    return {int(r["id"]): r for r in records if "id" in r}


def track_price_changes(
    current: List[Dict[str, Any]],
    previous: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    يقارن بين إصدارين ويقارن تغييرات الأسعار.
    يعيد قائمة بالأدوية التي تغيرت أسعارها مع تفاصيل التغيير.
    """
    prev_index = index_by_id(previous)
    changes: List[Dict[str, Any]] = []

    for curr in current:
        curr_id = int(curr.get("id", 0))
        prev = prev_index.get(curr_id)
        if not prev:
            continue  # دواء جديد في الإصدار الحالي

        curr_price = curr.get("price")
        prev_price = prev.get("price")

        if curr_price == prev_price:
            continue  # لا تغيير

        # أحد السعرين فارغ أو كلااهما غير رقمي
        try:
            curr_p = float(curr_price) if curr_price not in (None, "") else None
            prev_p = float(prev_price) if prev_price not in (None, "") else None
        except (ValueError, TypeError):
            continue

        if curr_p is None and prev_p is None:
            continue
        if curr_p is None:
            changes.append(
                {
                    "id": curr_id,
                    "name": curr.get("name"),
                    "arabic": curr.get("arabic"),
                    "company": curr.get("company"),
                    "old_price": prev_p,
                    "new_price": None,
                    "change_type": "price_removed",
                    "change_pct": None,
                    "barcode": curr.get("barcode"),
                }
            )
            continue
        if prev_p is None:
            changes.append(
                {
                    "id": curr_id,
                    "name": curr.get("name"),
                    "arabic": curr.get("arabic"),
                    "company": curr.get("company"),
                    "old_price": None,
                    "new_price": curr_p,
                    "change_type": "price_added",
                    "change_pct": None,
                    "barcode": curr.get("barcode"),
                }
            )
            continue

        if prev_p == 0:
            change_pct = None
            change_type = "price_changed_inf"
        else:
            change_pct = round((curr_p - prev_p) / prev_p * 100, 2)
            if curr_p > prev_p:
                change_type = "price_increased"
            elif curr_p < prev_p:
                change_type = "price_decreased"
            else:
                change_type = "price_unchanged"

        changes.append(
            {
                "id": curr_id,
                "name": curr.get("name"),
                "arabic": curr.get("arabic"),
                "company": curr.get("company"),
                "old_price": prev_p,
                "new_price": curr_p,
                "change_type": change_type,
                "change_pct": change_pct,
                "barcode": curr.get("barcode"),
            }
        )

    # ترتيب حسب نسبة التغيير تنازلياً (الأكبر تأثيراً أولاً)
    changes.sort(
        key=lambda x: abs(x["change_pct"] or 0) if x["change_pct"] is not None else -1,
        reverse=True,
    )
    return changes


def summarize_changes(changes: List[Dict[str, Any]]) -> Dict[str, Any]:
    increased = [c for c in changes if c["change_type"] == "price_increased"]
    decreased = [c for c in changes if c["change_type"] == "price_decreased"]
    added = [c for c in changes if c["change_type"] == "price_added"]
    removed = [c for c in changes if c["change_type"] == "price_removed"]

    def avg_pct(lst):
        vals = [c["change_pct"] for c in lst if c["change_pct"] is not None]
        return round(sum(vals) / len(vals), 2) if vals else None

    return {
        "total_changes": len(changes),
        "price_increased": len(increased),
        "price_decreased": len(decreased),
        "price_added": len(added),
        "price_removed": len(removed),
        "avg_increase_pct": avg_pct(increased),
        "avg_decrease_pct": avg_pct(decreased),
        "max_increase": max(
            [(c["change_pct"], c["arabic"], c["name"]) for c in increased],
            key=lambda x: x[0],
            default=None,
        ),
        "max_decrease": min(
            [(c["change_pct"], c["arabic"], c["name"]) for c in decreased],
            key=lambda x: x[0],
            default=None,
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="تتبع تغييرات أسعار الأدوية بين إصدارين من البيانات"
    )
    parser.add_argument(
        "--current",
        type=Path,
        default=DEFAULT_CURRENT,
        help="ملف البيانات الحالي (JSON)",
    )
    parser.add_argument(
        "--previous",
        type=Path,
        required=True,
        help="ملف البيانات السابق (المقارن)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="ملف مخرج تفاصيل التغييرات (JSON)",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=DEFAULT_SUMMARY,
        help="ملف مخرج الإحصائيات المجمعة (JSON)",
    )
    args = parser.parse_args()

    if not args.current.exists():
        print(f"خطأ: الملف الحالي غير موجود: {args.current}", file=sys.stderr)
        sys.exit(1)
    if not args.previous.exists():
        print(f"خطأ: الملف السابق غير موجود: {args.previous}", file=sys.stderr)
        sys.exit(1)

    current = load_json(args.current)
    previous = load_json(args.previous)

    changes = track_price_changes(current, previous)
    summary = summarize_changes(changes)

    args.output.write_text(
        json.dumps(changes, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    args.summary.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"تمت مقارنة {len(current)} سجل حالي مع {len(previous)} سجل سابق.")
    print(f"تم العثور على {len(changes)} تغيير في الأسعار.")
    print(f"  زيادات: {summary['price_increased']}")
    print(f"  نقصانات: {summary['price_decreased']}")
    print(f"  أسعار مضافة: {summary['price_added']}")
    print(f"  أسعار محذوفة: {summary['price_removed']}")
    print(f"تم حفظ التفاصيل في: {args.output}")
    print(f"تم حفظ الإحصائيات في: {args.summary}")


if __name__ == "__main__":
    main()
