"""
SentinelX EDR - Metrics API
"""

from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.metric import MetricDashboard, MttdResponse
from app.services.metrics_collector import get_dashboard_metrics, get_mttd

router = APIRouter()

@router.get("/dashboard", response_model=MetricDashboard)
def get_dashboard(db: Session = Depends(get_db)) -> Any:
    return get_dashboard_metrics(db)

@router.get("/mttd", response_model=MttdResponse)
def get_mttd_metric(db: Session = Depends(get_db)) -> Any:
    return get_mttd(db)
