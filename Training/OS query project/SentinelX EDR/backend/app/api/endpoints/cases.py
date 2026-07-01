"""
SentinelX EDR - Cases API
"""

from typing import List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.case import CaseCreate, CaseUpdate, CaseResponse, CaseNoteCreate, CaseNoteResponse, CaseEvidenceCreate, CaseEvidenceResponse
from app.services.case_manager import create_case, update_case, get_case, list_cases, add_note, get_notes, add_evidence, get_evidence

router = APIRouter()

@router.post("/", response_model=CaseResponse)
def api_create_case(data: CaseCreate, db: Session = Depends(get_db)) -> Any:
    return create_case(db, data)

@router.get("/", response_model=List[CaseResponse])
def api_list_cases(status: Optional[str] = None, priority: Optional[str] = None, db: Session = Depends(get_db)) -> Any:
    return list_cases(db, status=status, priority=priority)

@router.get("/{case_id}", response_model=CaseResponse)
def api_get_case(case_id: str, db: Session = Depends(get_db)) -> Any:
    case = get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@router.patch("/{case_id}", response_model=CaseResponse)
def api_update_case(case_id: str, data: CaseUpdate, db: Session = Depends(get_db)) -> Any:
    case = update_case(db, case_id, data)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@router.post("/{case_id}/notes", response_model=CaseNoteResponse)
def api_add_note(case_id: str, data: CaseNoteCreate, db: Session = Depends(get_db)) -> Any:
    return add_note(db, case_id, data)

@router.get("/{case_id}/notes", response_model=List[CaseNoteResponse])
def api_get_notes(case_id: str, db: Session = Depends(get_db)) -> Any:
    return get_notes(db, case_id)

@router.post("/{case_id}/evidence", response_model=CaseEvidenceResponse)
def api_add_evidence(case_id: str, data: CaseEvidenceCreate, db: Session = Depends(get_db)) -> Any:
    return add_evidence(db, case_id, data)

@router.get("/{case_id}/evidence", response_model=List[CaseEvidenceResponse])
def api_get_evidence(case_id: str, db: Session = Depends(get_db)) -> Any:
    return get_evidence(db, case_id)
