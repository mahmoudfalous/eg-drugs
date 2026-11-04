"""
Track price changes in the Egyptian Drug Database.

Compares two versions of drug data (current and previous) and produces a report
of all drugs whose prices changed, with the change percentage and direction
(increase/decrease).

Outputs:
- data/price_changes.json: list of all drugs with changed prices
- data/price_changes_summary.json: aggregated statistics

Usage:
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
    Compare two versions and return a list of drugs with changed prices,
    including change details.
    """
    prev_index = index_by_id(previous)
    changes: List[Dict[str, Any]] = []

    for curr in current:
        curr_id = int(curr.get("id", 0))
        prev = prev_index.get(curr_id)
        if not prev:
            continue  # new drug in current version

        curr_price = curr.get("price")
        prev_price = prev.get("price")

        if curr_price == prev_price:
            continue  # no change

        # one or both prices are empty or non-numeric
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

    # Sort by change percentage descending (highest impact first)
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
        description="Track drug price changes between two data versions"
    )
    parser.add_argument(
        "--current",
        type=Path,
        default=DEFAULT_CURRENT,
        help="Current data file (JSON)",
    )
    parser.add_argument(
        "--previous",
        type=Path,
        required=True,
        help="Previous data file to compare against (JSON)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output file for change details (JSON)",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=DEFAULT_SUMMARY,
        help="Output file for summary statistics (JSON)",
    )
    args = parser.parse_args()

    if not args.current.exists():
        print(f"Error: current file not found: {args.current}", file=sys.stderr)
        sys.exit(1)
    if not args.previous.exists():
        print(f"Error: previous file not found: {args.previous}", file=sys.stderr)
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

    print(f"Compared {len(current)} current records with {len(previous)} previous records.")
    print(f"Found {len(changes)} price changes.")
    print(f"  Increases: {summary['price_increased']}")
    print(f"  Decreases: {summary['price_decreased']}")
    print(f"  Prices added: {summary['price_added']}")
    print(f"  Prices removed: {summary['price_removed']}")
    print(f"Details saved to: {args.output}")
    print(f"Summary saved to: {args.summary}")


if __name__ == "__main__":
    main()
