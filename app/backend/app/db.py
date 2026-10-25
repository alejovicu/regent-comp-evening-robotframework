"""MongoDB access. Tests replace `get_db` with a mongomock database."""
from pymongo import ASCENDING, MongoClient
from pymongo.database import Database

from .config import settings

_client: MongoClient | None = None


def get_db() -> Database:
    global _client
    if _client is None:
        _client = MongoClient(settings.mongo_url, serverSelectionTimeoutMS=5000)
    return _client[settings.mongo_db]


def ensure_indexes(db: Database) -> None:
    db.users.create_index([("username", ASCENDING)], unique=True)
    db.products.create_index([("sku", ASCENDING)], unique=True)
    db.carts.create_index([("username", ASCENDING)], unique=True)
