from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.database import Database

from ..deps import get_database, require_user
from ..models import Cart, CartItemIn, CartItemUpdate, CartLine, CurrentUser
from .products import parse_id

router = APIRouter(prefix="/api/cart", tags=["cart"])


def build_cart(db: Database, username: str) -> Cart:
    doc = db.carts.find_one({"username": username}) or {"items": []}
    lines: list[CartLine] = []
    for item in doc["items"]:
        product = db.products.find_one({"_id": parse_id(item["product_id"])})
        if product is None:
            continue  # product was removed from the catalog
        lines.append(CartLine(
            product_id=item["product_id"],
            sku=product["sku"],
            name=product["name"],
            price=product["price"],
            quantity=item["quantity"],
            line_total=round(product["price"] * item["quantity"], 2),
        ))
    return Cart(
        username=username,
        items=lines,
        item_count=sum(line.quantity for line in lines),
        total=round(sum(line.line_total for line in lines), 2),
    )


@router.get("", response_model=Cart)
def get_cart(user: CurrentUser = Depends(require_user), db: Database = Depends(get_database)):
    return build_cart(db, user.username)


@router.post("/items", response_model=Cart)
def add_item(
    body: CartItemIn,
    user: CurrentUser = Depends(require_user),
    db: Database = Depends(get_database),
):
    if db.products.find_one({"_id": parse_id(body.product_id)}) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found")
    cart = db.carts.find_one({"username": user.username}) or {"items": []}
    items = cart["items"]
    for item in items:
        if item["product_id"] == body.product_id:
            item["quantity"] = min(item["quantity"] + body.quantity, 99)
            break
    else:
        items.append({"product_id": body.product_id, "quantity": body.quantity})
    db.carts.update_one({"username": user.username}, {"$set": {"items": items}}, upsert=True)
    return build_cart(db, user.username)


@router.put("/items/{product_id}", response_model=Cart)
def update_item(
    product_id: str,
    body: CartItemUpdate,
    user: CurrentUser = Depends(require_user),
    db: Database = Depends(get_database),
):
    result = db.carts.update_one(
        {"username": user.username, "items.product_id": product_id},
        {"$set": {"items.$.quantity": body.quantity}},
    )
    if result.matched_count == 0:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Item not in cart")
    return build_cart(db, user.username)


@router.delete("/items/{product_id}", response_model=Cart)
def remove_item(
    product_id: str,
    user: CurrentUser = Depends(require_user),
    db: Database = Depends(get_database),
):
    db.carts.update_one({"username": user.username}, {"$pull": {"items": {"product_id": product_id}}})
    return build_cart(db, user.username)


@router.delete("", response_model=Cart)
def clear_cart(user: CurrentUser = Depends(require_user), db: Database = Depends(get_database)):
    db.carts.update_one({"username": user.username}, {"$set": {"items": []}}, upsert=True)
    return build_cart(db, user.username)
