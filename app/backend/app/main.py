import logging
import time
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo.database import Database
from pymongo.errors import PyMongoError

from . import db as db_module
from .config import settings
from .deps import get_database
from .routers import admin, auth, cart, products
from .seed import seed

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    database = db_module.get_db()
    # MongoDB may still be starting when the backend pod comes up, so retry for a while.
    for attempt in range(1, 31):
        try:
            db_module.ensure_indexes(database)
            break
        except PyMongoError as exc:
            log.warning("MongoDB not ready (attempt %d/30): %s", attempt, exc)
            time.sleep(2)
    else:
        raise RuntimeError("MongoDB is not reachable")
    seed(database)
    yield


app = FastAPI(
    title="Shopping Cart Demo API",
    version="1.0.0",
    lifespan=lifespan,
    # Served under /api so the docs are reachable through the frontend nginx proxy.
    docs_url="/api/docs",
    redoc_url=None,
    openapi_url="/api/openapi.json",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(admin.router)


@app.get("/api/health", tags=["health"])
def health(db: Database = Depends(get_database)):
    db.command("ping")
    return {"status": "ok"}
