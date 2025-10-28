# app/repositories/sql_repo.py
from .session_repo import SessionRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from app.models.session_model import DBSession, SessionInfo
from typing import List, Optional
from datetime import datetime

class SQLSessionRepository(SessionRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, session: SessionInfo):
        db_session = DBSession(**session.dict())
        self.db.add(db_session)
        await self.db.commit()

    async def get(self, session_id: str) -> Optional[SessionInfo]:
        result = await self.db.execute(select(DBSession).where(DBSession.session_id == session_id))
        row = result.scalar_one_or_none()
        if row:
            data = {**row.__dict__}
            data["uptime_seconds"] = int((datetime.now() - data["created_at"]).total_seconds())
            return SessionInfo(**data)
        return None

    async def list_all(self) -> List[SessionInfo]:
        result = await self.db.execute(select(DBSession))
        sessions = []
        for row in result.scalars():
            data = {**row.__dict__}
            data["uptime_seconds"] = int((datetime.now() - data["created_at"]).total_seconds())
            sessions.append(SessionInfo(**data))
        return sessions

    async def delete(self, session_id: str) -> bool:
        result = await self.db.execute(delete(DBSession).where(DBSession.session_id == session_id))
        await self.db.commit()
        return result.rowcount > 0

    async def update_video_preview(self, session_id: str, url: str):
        await self.db.execute(
            update(DBSession)
            .where(DBSession.session_id == session_id)
            .values(video_preview_link=url)
        )
        await self.db.commit()