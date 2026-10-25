from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException, Response, status
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError

from ..deps import get_current_user, get_database, require_admin
from ..models import Product, ProductIn, ProductUpdate

router = APIRouter(prefix="/api/products", tags=["products"])


def to_product(doc: dict) -> Product:
    return Product(
        id=str(doc["_id"]),
        sku=doc["sku"],
        name=doc["name"],
        price=doc["price"],
        description=doc.get("description", ""),
    )


def parse_id(product_id: str) -> ObjectId:
    try:
        return ObjectId(product_id)
    except (InvalidId, TypeError):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found")


@router.get("", response_model=list[Product], dependencies=[Depends(get_current_user)])
def list_products(q: str | None = None, db: Database = Depends(get_database)):
    query = {}
    if q:
        query = {"$or": [
            {"name": {"$regex": q, "$options": "i"}},
            {"sku": {"$regex": q, "$options": "i"}},
        ]}
    return [to_product(d) for d in db.products.find(query).sort("sku")]


@router.get("/{product_id}", response_model=Product, dependencies=[Depends(get_current_user)])
def get_product(product_id: str, db: Database = Depends(get_database)):
    doc = db.products.find_one({"_id": parse_id(product_id)})
    if doc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found")
    return to_product(doc)


@router.post("", response_model=Product, status_code=201, dependencies=[Depends(require_admin)])
def create_product(body: ProductIn, db: Database = Depends(get_database)):
    doc = body.model_dump()
    doc["price"] = round(doc["price"], 2)
    try:
        result = db.products.insert_one(doc)
    except DuplicateKeyError:
        raise HTTPException(status.HTTP_409_CONFLICT, f"SKU {body.sku} already exists")
    doc["_id"] = result.inserted_id
    return to_product(doc)


@router.put("/{product_id}", response_model=Product, dependencies=[Depends(require_admin)])
def update_product(product_id: str, body: ProductUpdate, db: Database = Depends(get_database)):
    oid = parse_id(product_id)
    changes = body.model_dump()
    changes["price"] = round(changes["price"], 2)
    result = db.products.update_one({"_id": oid}, {"$set": changes})
    if result.matched_count == 0:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found")
    return to_product(db.products.find_one({"_id": oid}))


@router.delete("/{product_id}", status_code=204, dependencies=[Depends(require_admin)])
def delete_product(product_id: str, db: Database = Depends(get_database)):
    oid = parse_id(product_id)
    if db.products.delete_one({"_id": oid}).deleted_count == 0:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found")
    db.carts.update_many({}, {"$pull": {"items": {"product_id": product_id}}})
    return Response(status_code=204)
