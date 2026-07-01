"""
SentinelX EDR - Simulations API
"""

from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.simulation import SimulationStart, SimulationResponse
from app.services.attack_simulator import start_simulation, list_scenarios, get_simulation

router = APIRouter()

@router.get("/scenarios")
def api_list_scenarios() -> Any:
    return list_scenarios()

@router.post("/run", response_model=SimulationResponse)
def api_run_simulation(data: SimulationStart, db: Session = Depends(get_db)) -> Any:
    try:
        return start_simulation(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{sim_id}", response_model=SimulationResponse)
def api_get_simulation(sim_id: str, db: Session = Depends(get_db)) -> Any:
    sim = get_simulation(db, sim_id)
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return sim
