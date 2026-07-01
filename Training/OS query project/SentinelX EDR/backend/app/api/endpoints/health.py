from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api import deps
from app.services.scheduler import scheduler_instance
import psutil
import time

router = APIRouter()

start_time = time.time()

@router.get("/")
def check_health(db: Session = Depends(deps.get_db)):
    health_status = {
        "status": "healthy",
        "uptime_seconds": int(time.time() - start_time),
        "database": "online",
        "scheduler": "running" if scheduler_instance.scheduler.running else "stopped",
        "system": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent
        }
    }
    
    # Check DB
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
    except Exception as e:
        health_status["database"] = f"offline: {str(e)}"
        health_status["status"] = "degraded"
        
    return health_status
