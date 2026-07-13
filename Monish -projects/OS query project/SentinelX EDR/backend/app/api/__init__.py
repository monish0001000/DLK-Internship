"""
SentinelX EDR - API Routers Package
"""

from fastapi import APIRouter

from app.api.endpoints import endpoints
from app.api.endpoints import telemetry
from app.api.endpoints import alerts
from app.api.endpoints import investigations
from app.api.endpoints import cases
from app.api.endpoints import rules
from app.api.endpoints import metrics
from app.api.endpoints import threat_intel
from app.api.endpoints import simulations
from app.api.endpoints import websocket
from app.api.endpoints import threat_hunting
from app.api.endpoints import graphs
from app.api.endpoints import responses
from app.api.endpoints import health
from app.api.endpoints import auth
from app.api.endpoints import audit

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])

api_router.include_router(endpoints.router, prefix="/endpoints", tags=["endpoints"])
api_router.include_router(telemetry.router, prefix="/telemetry", tags=["telemetry"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(investigations.router, prefix="/investigations", tags=["investigations"])
api_router.include_router(cases.router, prefix="/cases", tags=["cases"])
api_router.include_router(rules.router, prefix="/rules", tags=["rules"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
api_router.include_router(threat_intel.router, prefix="/threat-intel", tags=["threat-intel"])
api_router.include_router(simulations.router, prefix="/simulations", tags=["simulations"])
api_router.include_router(threat_hunting.router, prefix="/threat-hunting", tags=["threat-hunting"])
api_router.include_router(graphs.router, prefix="/graphs", tags=["graphs"])
api_router.include_router(responses.router, prefix="/responses", tags=["responses"])
api_router.include_router(websocket.router, tags=["websocket"])
