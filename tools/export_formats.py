"""
تصدير بيانات الأدوية إلى صيغ إضافية:
- Excel (.xlsx) عبر pandas + openpyxl
- Parquet (.parquet) عبر pandas + pyarrow (إذا كان مثبتاً)

تشغيل:
    python tools/export_formats.py --input data/eg_drugs.json --output-dir data/exports
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

try:
    import pandas as pd

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import pyarrow  # noqa: F401

    PARQUET_AVAILABLE = True
except ImportError:
    PARQUET_AVAILABLE = False

DEFAULT_INPUT = Path(__file__).resolve().parent.parent / "data" / "eg_drugs.json"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "exports"


import re

_CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]")


def _clean_text(value: Any) -> Any:
    """إزالة أحرف التحكم غير الصالحة في ملفات Excel/XML."""
    if isinstance(value, str):
        return _CONTROL_CHARS_RE.sub("", value)
    return value


def load_json(path: Path) -> List[Dict[str, Any]]:
    with open(path, encoding="utf-8-sig") as f:
        return json.load(f)


def export_to_excel(records: List[Dict[str, Any]], output_path: Path) -> None:
    if not PANDAS_AVAILABLE:
        raise ImportError("pandas غير مثبت. قم بتثبيته: pip install pandas openpyxl")
    cleaned = [{k: _clean_text(v) for k, v in r.items()} for r in records]
    df = pd.DataFrame(cleaned)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(output_path, index=False, engine="openpyxl")
    print(f"تم التصدير إلى Excel: {output_path} ({len(df)} سجل)")


def export_to_parquet(records: List[Dict[str, Any]], output_path: Path) -> None:
    if not PANDAS_AVAILABLE:
        raise ImportError("pandas غير مثبت. قم بتثبيته: pip install pandas")
    if not PARQUET_AVAILABLE:
        raise ImportError(
            "pyarrow غير مثبت. قم بتثبيته: pip install pyarrow ( مطلوب لـ Parquet )"
        )
    df = pd.DataFrame(records)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)
    print(f"تم التصدير إلى Parquet: {output_path} ({len(df)} سجل)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="تصدير بيانات الأدوية إلى صيغ إضافية (Excel, Parquet)"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="ملف البيانات المدخل (JSON)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="مجلد المخرجات",
    )
    parser.add_argument(
        "--excel",
        action="store_true",
        help="تصدير إلى Excel (.xlsx)",
    )
    parser.add_argument(
        "--parquet",
        action="store_true",
        help="تصدير إلى Parquet (.parquet)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="تصدير إلى جميع الصيغ المتاحة",
    )
    args = parser.parse_args()

    if not PANDAS_AVAILABLE:
        print("خطأ: pandas غير مثبت. قم بتثبيته: pip install pandas openpyxl", file=sys.stderr)
        sys.exit(1)

    if not args.input.exists():
        print(f"خطأ: ملف الإدخال غير موجود: {args.input}", file=sys.stderr)
        sys.exit(1)

    args.output_dir.mkdir(parents=True, exist_ok=True)

    records = load_json(args.input)

    do_excel = args.excel or args.all
    do_parquet = args.parquet or args.all

    if do_excel:
        export_to_excel(records, args.output_dir / "eg_drugs.xlsx")

    if do_parquet:
        try:
            export_to_parquet(records, args.output_dir / "eg_drugs.parquet")
        except ImportError as e:
            print(f"تخطي Parquet: {e}", file=sys.stderr)

    if not do_excel and not do_parquet:
        print("لا توجد صيغة محددة للتصدير. استخدم --excel أو --parquet أو --all.")
        sys.exit(1)


if __name__ == "__main__":
    main()
