from fastapi import APIRouter
from datetime import datetime
from app.services.browser_manager import browser_manager
from app.config import settings
from app.utils.port_helper import port_allocator
from app.models.session_model import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring API and Playwright readiness."""
    active_sessions = len(browser_manager.list_sessions())
    available_ports = port_allocator.get_available_count()
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        uptime_seconds=browser_manager.get_uptime_seconds(),
        active_sessions=active_sessions,
        max_sessions=settings.max_browsers,
        available_ports=available_ports
    )

