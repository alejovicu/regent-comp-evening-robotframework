"""Parse catalog CSV files and apply them to the products collection.

Expected header (order does not matter, description is optional):

    sku,name,price,description
"""
import csv
import io

from pydantic import ValidationError
from pymongo.database import Database

from .models import IngestionResult, ProductIn, RowError

REQUIRED_COLUMNS = {"sku", "name", "price"}


class CatalogFormatError(ValueError):
    pass


def parse_catalog(text: str) -> tuple[list[ProductIn], list[RowError]]:
    reader = csv.DictReader(io.StringIO(text.lstrip("﻿")))
    columns = {c.strip().lower() for c in (reader.fieldnames or [])}
    missing = REQUIRED_COLUMNS - columns
    if missing:
        raise CatalogFormatError(f"Missing column(s): {', '.join(sorted(missing))}")

    products: list[ProductIn] = []
    errors: list[RowError] = []
    seen: set[str] = set()
    for line_no, raw in enumerate(reader, start=2):
        row = {(k or "").strip().lower(): (v or "").strip() for k, v in raw.items()}
        if not any(row.values()):
            continue
        try:
            product = ProductIn(
                sku=row.get("sku", ""),
                name=row.get("name", ""),
                price=row.get("price", ""),
                description=row.get("description", ""),
            )
        except ValidationError as exc:
            first = exc.errors()[0]
            field = ".".join(str(p) for p in first["loc"])
            errors.append(RowError(line=line_no, error=f"{field}: {first['msg']}"))
            continue
        if product.sku in seen:
            errors.append(RowError(line=line_no, error=f"sku: duplicate {product.sku}"))
            continue
        seen.add(product.sku)
        products.append(product)
    return products, errors


def apply_catalog(
    db: Database, filename: str, text: str, replace: bool = False
) -> IngestionResult:
    products, errors = parse_catalog(text)
    created = updated = deleted = 0
    for p in products:
        result = db.products.update_one(
            {"sku": p.sku},
            {"$set": {"name": p.name, "price": round(p.price, 2), "description": p.description}},
            upsert=True,
        )
        if result.upserted_id is not None:
            created += 1
        elif result.modified_count:
            updated += 1
    if replace:
        skus = [p.sku for p in products]
        deleted = db.products.delete_many({"sku": {"$nin": skus}}).deleted_count
    return IngestionResult(
        filename=filename,
        replace=replace,
        created=created,
        updated=updated,
        deleted=deleted,
        errors=errors,
    )
