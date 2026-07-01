"""
SentinelX EDR - FastAPI Main Entry Point
"""

import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import engine, Base, SessionLocal
from app.api import api_router
from app.services.detection.engine import engine as detection_engine
from app.core.websocket_manager import ws_manager as manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("SentinelX")

# Create database tables
Base.metadata.create_all(bind=engine)

from app.services.scheduler import scheduler_instance

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting SentinelX EDR Backend...")
    settings = get_settings()
    
    # Initialize Detection Engine
    db = SessionLocal()
    try:
        detection_engine.initialize(db, settings)
        
        # Connect the engine to the websocket manager to broadcast new alerts
        def broadcast_alert(alert):
            import json
            # Fire-and-forget async broadcast from sync callback
            alert_data = {
                "type": "new_alert",
                "data": {
                    "id": alert.id,
                    "title": alert.title,
                    "severity": alert.severity,
                    "endpoint_id": alert.endpoint_id
                }
            }
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(manager.broadcast(json.dumps(alert_data)))
            except RuntimeError:
                pass # No running loop (e.g. tests)
                
        detection_engine.on_alert(broadcast_alert)
        
    finally:
        db.close()
        
    # Start background scheduler
    scheduler_instance.start()
        
    yield
    
    # Shutdown
    scheduler_instance.shutdown()
    logger.info("Shutting down SentinelX EDR Backend...")

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered Endpoint Detection and Response Platform",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "project": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "docs_url": "/docs"
    }
