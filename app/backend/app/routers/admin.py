from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.database import Database

from .. import sftp_client
from ..catalog import CatalogFormatError, apply_catalog
from ..deps import get_database, require_admin
from ..models import CurrentUser, IngestionRequest, IngestionResult
from ..seed import SAMPLE_PRODUCTS

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/sftp/files", dependencies=[Depends(require_admin)])
def list_sftp_files():
    try:
        return sftp_client.list_files()
    except sftp_client.SftpError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(exc))


@router.post("/ingest", response_model=IngestionResult)
def ingest_catalog(
    body: IngestionRequest,
    user: CurrentUser = Depends(require_admin),
    db: Database = Depends(get_database),
):
    try:
        text = sftp_client.read_file(body.filename)
    except sftp_client.SftpError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(exc))
    try:
        result = apply_catalog(db, body.filename, text, replace=body.replace)
    except CatalogFormatError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc))
    db.ingestions.insert_one({
        **result.model_dump(),
        "by": user.username,
        "at": datetime.now(timezone.utc).isoformat(),
    })
    return result


@router.get("/ingestions", dependencies=[Depends(require_admin)])
def ingestion_history(db: Database = Depends(get_database)):
    return list(db.ingestions.find({}, {"_id": 0}).sort("at", -1).limit(20))


@router.post("/reset", dependencies=[Depends(require_admin)])
def reset_demo_data(db: Database = Depends(get_database)):
    """Restore the sample catalog and empty every cart. Handy as a test setup step."""
    db.products.delete_many({})
    db.products.insert_many([dict(p) for p in SAMPLE_PRODUCTS])
    db.carts.delete_many({})
    db.ingestions.delete_many({})
    return {"status": "reset", "products": len(SAMPLE_PRODUCTS)}
