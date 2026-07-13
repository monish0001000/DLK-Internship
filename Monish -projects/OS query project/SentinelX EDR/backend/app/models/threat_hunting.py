from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from app.database import Base

class SavedHunt(Base):
    __tablename__ = "saved_hunts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String, nullable=True)
    query_payload = Column(JSON) # The structured JSON query
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class HuntHistory(Base):
    __tablename__ = "hunt_history"

    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(String)
    query_payload = Column(JSON)
    user = Column(String)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
