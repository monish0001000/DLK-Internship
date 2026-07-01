"""
SentinelX EDR - Threat Intel API
"""

from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.threat_intel import FeedSyncRequest, FeedSyncResponse
from app.services.threat_intel_service import sync_abuseipdb, sync_otx, sync_malwarebazaar, get_ioc_stats

router = APIRouter()

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)) -> Any:
    return get_ioc_stats(db)

@router.post("/sync", response_model=FeedSyncResponse)
def sync_feed(data: FeedSyncRequest, db: Session = Depends(get_db)) -> Any:
    feed = data.feed_name.lower()
    if feed == "abuseipdb":
        return sync_abuseipdb(db, "")
    elif feed == "otx":
        return sync_otx(db, "")
    elif feed == "malwarebazaar":
        return sync_malwarebazaar(db)
    else:
        return {"feed_name": feed, "iocs_added": 0, "iocs_updated": 0, "status": "unsupported"}
