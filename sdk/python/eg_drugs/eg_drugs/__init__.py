"""
eg-drugs Python SDK
===================
Python library for accessing the Egyptian Drug Database (eg-drugs).

Search drugs by name (Arabic/English), active ingredient, company, or barcode,
and find generic alternatives (same active ingredient).

Quick example:
    from eg_drugs import search, get_by_id, get_by_barcode, get_generics

    results = search("panadol", limit=5)
    for drug in results:
        print(drug.arabic, drug.price)
"""

from .client import EgDrugsClient, search, search_by_active, search_by_company
from .client import get_by_id, get_by_barcode, get_generics, load_stats
from .models import Drug, Stats

__all__ = [
    "EgDrugsClient",
    "Drug",
    "Stats",
    "search",
    "search_by_active",
    "search_by_company",
    "get_by_id",
    "get_by_barcode",
    "get_generics",
    "load_stats",
]

__version__ = "1.0.0"
