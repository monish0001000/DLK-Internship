"""
SentinelX EDR - Pydantic Schemas Package
=========================================
Exports all Pydantic schemas used for API request validation
and response serialization.
"""

from app.schemas.endpoint import EndpointCreate, EndpointUpdate, EndpointResponse, EndpointHeartbeat
from app.schemas.telemetry import (
    TelemetryIngest, ProcessData, NetworkData, StartupData,
    ServiceData, TaskData, SessionData, TelemetryQuery
)
from app.schemas.alert import AlertCreate, AlertUpdate, AlertResponse, AlertFilter
from app.schemas.investigation import InvestigationTrigger, InvestigationResponse
from app.schemas.threat_hunting import ThreatHuntQuery, ThreatHuntSaveRequest, SavedHuntResponse, ThreatHuntHistory
from app.schemas.response_log import ResponseActionRequest, ResponseLogResponse
from app.schemas.user import UserCreate, UserUpdate, UserResponse, Token, TokenData
from app.schemas.audit import AuditLogCreate, AuditLogResponse
from app.schemas.case import (
    CaseCreate, CaseUpdate, CaseResponse,
    CaseNoteCreate, CaseNoteResponse,
    CaseEvidenceCreate, CaseEvidenceResponse
)
from app.schemas.report import ReportGenerate, ReportResponse
from app.schemas.threat_intel import (
    ThreatIntelCreate, ThreatIntelResponse, ThreatIntelBulkImport,
    FeedSyncRequest, FeedSyncResponse
)
from app.schemas.detection_rule import (
    DetectionRuleCreate, DetectionRuleUpdate, DetectionRuleResponse, RuleImport
)
from app.schemas.metric import MetricDashboard, MttdResponse
from app.schemas.simulation import SimulationScenario, SimulationStart, SimulationResponse
from app.schemas.graph import GraphNode, GraphEdge, ThreatGraph

__all__ = [
    "EndpointCreate", "EndpointUpdate", "EndpointResponse", "EndpointHeartbeat",
    "TelemetryIngest", "ProcessData", "NetworkData", "StartupData",
    "ServiceData", "TaskData", "SessionData", "TelemetryQuery",
    "AlertCreate", "AlertUpdate", "AlertResponse", "AlertFilter",
    "InvestigationTrigger", "InvestigationResponse",
    "CaseCreate", "CaseUpdate", "CaseResponse",
    "CaseNoteCreate", "CaseNoteResponse",
    "CaseEvidenceCreate", "CaseEvidenceResponse",
    "ReportGenerate", "ReportResponse",
    "ThreatIntelCreate", "ThreatIntelResponse", "ThreatIntelBulkImport",
    "FeedSyncRequest", "FeedSyncResponse",
    "DetectionRuleCreate", "DetectionRuleUpdate", "DetectionRuleResponse", "RuleImport",
    "MetricDashboard", "MttdResponse",
    "SimulationScenario", "SimulationStart", "SimulationResponse",
    "GraphNode", "GraphEdge", "ThreatGraph",
]
