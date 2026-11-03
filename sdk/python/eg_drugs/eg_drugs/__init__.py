"""
eg-drugs Python SDK
===================
مكتبة Python للوصول إلى قاعدة بيانات الأدوية المصرية (eg-drugs).

البحث بالأسماء العربية أو الإنجليزية، المادة الفعالة، الشركة، أو الباركود،
وإيجاد الأدوية البديلة (نفس المادة الفعالة).

مثال سريع:
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
