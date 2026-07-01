from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Text
from app.database import Base

class ResponseLog(Base):
    __tablename__ = "response_logs"

    id = Column(Integer, primary_key=True, index=True)
    endpoint_id = Column(String, index=True)
    user = Column(String)
    action_requested = Column(String)
    execution_mode = Column(String)  # 'live' or 'simulation'
    status = Column(String)          # 'success', 'failed', 'simulated'
    reason = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
