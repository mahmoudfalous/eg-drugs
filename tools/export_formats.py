"""
Export drug data to additional formats:
- Excel (.xlsx) via pandas + openpyxl
- Parquet (.parquet) via pandas + pyarrow (if installed)

Usage:
    python tools/export_formats.py --input data/eg_drugs.json --output-dir data/exports
"""

from __future__ import annotations

import argparse
import json
import re
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

_CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]")


def _clean_text(value: Any) -> Any:
    """Remove control characters invalid in Excel/XML files."""
    if isinstance(value, str):
        return _CONTROL_CHARS_RE.sub("", value)
    return value


def load_json(path: Path) -> List[Dict[str, Any]]:
    with open(path, encoding="utf-8-sig") as f:
        return json.load(f)


def export_to_excel(records: List[Dict[str, Any]], output_path: Path) -> None:
    if not PANDAS_AVAILABLE:
        raise ImportError("pandas is not installed. Install it: pip install pandas openpyxl")
    cleaned = [{k: _clean_text(v) for k, v in r.items()} for r in records]
    df = pd.DataFrame(cleaned)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(output_path, index=False, engine="openpyxl")
    print(f"Exported to Excel: {output_path} ({len(df)} records)")


def export_to_parquet(records: List[Dict[str, Any]], output_path: Path) -> None:
    if not PANDAS_AVAILABLE:
        raise ImportError("pandas is not installed. Install it: pip install pandas")
    if not PARQUET_AVAILABLE:
        raise ImportError(
            "pyarrow is not installed. Install it: pip install pyarrow (required for Parquet)"
        )
    df = pd.DataFrame(records)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)
    print(f"Exported to Parquet: {output_path} ({len(df)} records)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export drug data to additional formats (Excel, Parquet)"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Input data file (JSON)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Output directory",
    )
    parser.add_argument(
        "--excel",
        action="store_true",
        help="Export to Excel (.xlsx)",
    )
    parser.add_argument(
        "--parquet",
        action="store_true",
        help="Export to Parquet (.parquet)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Export to all available formats",
    )
    args = parser.parse_args()

    if not PANDAS_AVAILABLE:
        print("Error: pandas is not installed. Install it: pip install pandas openpyxl", file=sys.stderr)
        sys.exit(1)

    if not args.input.exists():
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
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
            print(f"Skipping Parquet: {e}", file=sys.stderr)

    if not do_excel and not do_parquet:
        print("No export format specified. Use --excel, --parquet, or --all.")
        sys.exit(1)


if __name__ == "__main__":
    main()
