"""
Data models for the eg-drugs library.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class Drug:
    """A single drug model."""
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

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Drug":
        return cls(
            id=int(data.get("id", 0)),
            name=str(data.get("name", "")),
            arabic=str(data.get("arabic", "")),
            active=data.get("active"),
            company=data.get("company"),
            price=data.get("price"),
            oldprice=data.get("oldprice"),
            barcode=data.get("barcode"),
            barcode_valid=data.get("barcode_valid"),
            slug=data.get("slug"),
            units=data.get("units"),
            description=data.get("description"),
            uses=data.get("uses"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "arabic": self.arabic,
            "active": self.active,
            "company": self.company,
            "price": self.price,
            "oldprice": self.oldprice,
            "barcode": self.barcode,
            "barcode_valid": self.barcode_valid,
            "slug": self.slug,
            "units": self.units,
            "description": self.description,
            "uses": self.uses,
        }

    def __repr__(self) -> str:
        return f"<Drug id={self.id} name={self.name!r} arabic={self.arabic!r}>"


@dataclass
class Stats:
    """Database statistics."""
    total_drugs: int
    unique_companies: int
    unique_categories: int
    unique_active_ingredients: int
    valid_barcodes: int
    price_changed: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Stats":
        return cls(**data)

    def __repr__(self) -> str:
        return (
            f"<Stats total_drugs={self.total_drugs} "
            f"companies={self.unique_companies} "
            f"categories={self.unique_categories}>"
        )
