"""
SentinelX EDR - Response API
"""

from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.response_log import ResponseActionRequest, ResponseLogResponse
from app.services.response_simulator import simulate_response, get_response_log

router = APIRouter()

@router.post("/simulate", response_model=ResponseLogResponse)
def api_simulate_response(data: ResponseActionRequest, db: Session = Depends(get_db)) -> Any:
    try:
        # User is hardcoded to "system" for now until auth is added in phase 13
        result = simulate_response(
            db=db,
            action_type=data.action_type,
            target=data.target,
            endpoint_id=data.endpoint_id,
            user="admin_user", # mock user
            execution_mode=data.execution_mode,
            reason=data.reason
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs", response_model=List[ResponseLogResponse])
def api_get_response_logs(endpoint_id: str = None, db: Session = Depends(get_db)) -> Any:
    return get_response_log(db, endpoint_id)
