# app/repositories/mongo_repo.py
from .session_repo import SessionRepository
from motor.motor_asyncio import AsyncIOMotorCollection
from app.models.session_model import SessionInfo
from typing import List, Optional
from datetime import datetime

class MongoSessionRepository(SessionRepository):
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def create(self, session: SessionInfo):
        await self.collection.insert_one(session.dict())

    async def get(self, session_id: str) -> Optional[SessionInfo]:
        doc = await self.collection.find_one({"session_id": session_id})
        if doc:
            doc["uptime_seconds"] = int((datetime.now() - doc["created_at"]).total_seconds())
            return SessionInfo(**doc)
        return None

    async def list_all(self) -> List[SessionInfo]:
        cursor = self.collection.find({})
        sessions = []
        async for doc in cursor:
            doc["uptime_seconds"] = int((datetime.now() - doc["created_at"]).total_seconds())
            sessions.append(SessionInfo(**doc))
        return sessions

    async def delete(self, session_id: str) -> bool:
        result = await self.collection.delete_one({"session_id": session_id})
        return result.deleted_count > 0

    async def update_video_preview(self, session_id: str, url: str):
        await self.collection.update_one(
            {"session_id": session_id},
            {"$set": {"video_preview_link": url}}
        )