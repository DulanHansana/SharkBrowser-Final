# app/routes/sessions.py
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.services.browser_manager import browser_manager
from app.repositories.session_repo import SessionRepository
from app.db import get_repository
from app.models.session_model import (
    SessionCreateRequest,
    SessionCreateResponse,
    SessionListResponse,
    SessionReleaseRequest,
    SessionReleaseResponse,
    SessionInfo,
    ErrorResponse
)

router = APIRouter(prefix="/v1/sessions", tags=["sessions"])


@router.get("/", response_model=SessionListResponse)
async def list_sessions(repo: SessionRepository = Depends(get_repository)):
    """List all active browser sessions."""
    sessions = await browser_manager.list_sessions(repo)
    return SessionListResponse(
        sessions=sessions,
        total_count=len(sessions)
    )


@router.post("/", response_model=SessionCreateResponse)
async def create_session(
    request: SessionCreateRequest,
    repo: SessionRepository = Depends(get_repository)
):
    """Create a new browser session and return WebSocket URL."""
    try:
        session_info = await browser_manager.create_session(repo, request.session_id)
        
        if not session_info:
            if request.session_id and request.session_id in [s.session_id for s in await browser_manager.list_sessions(repo)]:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Session with ID '{request.session_id}' already exists"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Unable to create session. Maximum sessions reached or no ports available."
                )
        
        return SessionCreateResponse(
            session_id=session_info.session_id,
            port=session_info.port,
            cdp_endpoint=session_info.cdp_endpoint,
            cdp_websocket_url=session_info.cdp_websocket_url,
            cdp_discovery_url=session_info.cdp_discovery_url,
            message=f"Session '{session_info.session_id}' created successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}"
        )


@router.post("/release", response_model=SessionReleaseResponse)
async def release_session(
    request: SessionReleaseRequest,
    repo: SessionRepository = Depends(get_repository)
):
    """Release a browser session."""
    try:
        success = await browser_manager.release_session(repo, request.session_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session '{request.session_id}' not found"
            )
        
        return SessionReleaseResponse(
            session_id=request.session_id,
            message=f"Session '{request.session_id}' released successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to release session: {str(e)}"
        )


@router.get("/{session_id}", response_model=SessionInfo)
async def get_session(
    session_id: str,
    repo: SessionRepository = Depends(get_repository)
):
    """Get information about a specific session."""
    session_info = await browser_manager.get_session(repo, session_id)
    
    if not session_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found"
        )
    
    return session_info


@router.post("/multiple", response_model=dict)
async def create_multiple_browsers(repo: SessionRepository = Depends(get_repository)):
    """Create 5 browser sessions at once."""
    try:
        result = await browser_manager.create_multiple_browsers(repo, count=5)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create multiple browsers: {str(e)}"
        )


@router.post("/cleanup", response_model=dict)
async def cleanup_all_sessions(repo: SessionRepository = Depends(get_repository)):
    """Clean up all browser sessions."""
    try:
        await browser_manager.cleanup_all(repo)
        return {"message": "All sessions cleaned up successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cleanup sessions: {str(e)}"
        )