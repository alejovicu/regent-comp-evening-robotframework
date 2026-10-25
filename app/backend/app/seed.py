"""Seed demo users and products on startup."""
import logging

from pymongo.database import Database

from .config import settings
from .security import hash_password

log = logging.getLogger(__name__)

SAMPLE_PRODUCTS = [
    {"sku": "BOOK-001", "name": "Robot Framework Handbook", "price": 29.90, "description": "Paperback guide to keyword-driven testing"},
    {"sku": "MUG-001", "name": "Coffee Mug", "price": 9.50, "description": "Ceramic mug, 350 ml"},
    {"sku": "TSHIRT-001", "name": "Tester T-Shirt", "price": 19.99, "description": "Cotton t-shirt with a bug print"},
    {"sku": "KEYB-001", "name": "Mechanical Keyboard", "price": 89.00, "description": "Tenkeyless, brown switches"},
    {"sku": "MOUSE-001", "name": "Wireless Mouse", "price": 24.75, "description": "2.4 GHz with USB receiver"},
    {"sku": "STICK-001", "name": "Sticker Pack", "price": 4.99, "description": "Ten assorted laptop stickers"},
]


def seed(db: Database) -> None:
    for entry in filter(None, (s.strip() for s in settings.seed_users.split(","))):
        username, password, role = entry.split(":")
        if db.users.find_one({"username": username}) is None:
            db.users.insert_one(
                {"username": username, "password_hash": hash_password(password), "role": role}
            )
            log.info("Seeded user %s (%s)", username, role)
    if settings.seed_products and db.products.count_documents({}) == 0:
        db.products.insert_many([dict(p) for p in SAMPLE_PRODUCTS])
        log.info("Seeded %d sample products", len(SAMPLE_PRODUCTS))
