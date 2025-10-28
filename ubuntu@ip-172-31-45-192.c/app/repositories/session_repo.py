# app/repositories/session_repo.py
from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.session_model import SessionInfo

class SessionRepository(ABC):
    @abstractmethod
    async def create(self, session: SessionInfo) -> None: ...

    @abstractmethod
    async def get(self, session_id: str) -> Optional[SessionInfo]: ...

    @abstractmethod
    async def list_all(self) -> List[SessionInfo]: ...

    @abstractmethod
    async def delete(self, session_id: str) -> bool: ...

    @abstractmethod
    async def update_video_preview(self, session_id: str, url: str) -> None: ...