from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.sql import func
from app.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    user = Column(String, index=True, nullable=True) # Username or "System"
    ip_address = Column(String, nullable=True)
    action = Column(String, index=True, nullable=False) # e.g., "User Login", "Rule Created"
    object = Column(String, nullable=True) # e.g., "Rule ID 5", "Endpoint win-123"
    status = Column(String, nullable=False) # "Success", "Failed"
    execution_time_ms = Column(Float, nullable=True)
