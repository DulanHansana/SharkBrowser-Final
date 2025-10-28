from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from sqlalchemy import Column, String, Integer, DateTime, func
from app.db import Base  # ← will create later

class SessionCreateRequest(BaseModel):
    """Request model for creating a new browser session."""
    session_id: Optional[str] = None


class SessionInfo(BaseModel):
    """Information about a browser session."""
    session_id: str
    port: int
    cdp_endpoint: str
    cdp_websocket_url: Optional[str] = None
    cdp_discovery_url: Optional[str] = None
    created_at: datetime
    uptime_seconds: int
    status: str = "active"
    video_preview_link: Optional[str] = None


class SessionListResponse(BaseModel):
    """Response model for listing sessions."""
    sessions: List[SessionInfo]
    total_count: int


class SessionCreateResponse(BaseModel):
    """Response model for creating a session."""
    session_id: str
    port: int
    cdp_endpoint: str
    cdp_websocket_url: Optional[str] = None
    cdp_discovery_url: Optional[str] = None
    message: str


class SessionReleaseRequest(BaseModel):
    """Request model for releasing a session."""
    session_id: str


class SessionReleaseResponse(BaseModel):
    """Response model for releasing a session."""
    session_id: str
    message: str


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    timestamp: datetime
    uptime_seconds: int
    active_sessions: int
    max_sessions: int
    available_ports: int


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None


class DBSession(Base):
    __tablename__ = "sessions"
    session_id = Column(String, primary_key=True)
    port = Column(Integer)
    cdp_endpoint = Column(String)
    cdp_websocket_url = Column(String, nullable=True)
    cdp_discovery_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    status = Column(String, default="active")
    video_preview_link = Column(String, nullable=True)

