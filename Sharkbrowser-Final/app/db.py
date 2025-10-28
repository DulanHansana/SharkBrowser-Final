# app/db.py
from app.config import settings
from app.repositories.session_repo import SessionRepository
from app.repositories.mongo_repo import MongoSessionRepository
from app.repositories.sql_repo import SQLSessionRepository
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# SQLAlchemy
engine = None
SessionLocal = None

async def get_repository() -> SessionRepository:
    if settings.database_type == "mongodb":
        client = AsyncIOMotorClient(settings.database_url)
        db = client[settings.mongodb_db_name or "sharkbrowser"]
        collection = db["sessions"]
        await collection.create_index("session_id", unique=True)
        return MongoSessionRepository(collection)

    elif settings.database_type in ["postgresql", "sqlite", "mysql"]:
        global engine, SessionLocal
        if engine is None:
            url = settings.database_url
            if settings.database_type == "sqlite":
                url = url.replace("sqlite://", "sqlite+aiosqlite://")
            elif settings.database_type == "mysql":
                url = url.replace("mysql://", "mysql+aiomysql://")
            engine = create_async_engine(url, echo=False)
            SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with SessionLocal() as session:
            from app.models.session_model import Base
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            return SQLSessionRepository(session)

    else:
        raise ValueError(f"Unsupported DATABASE_TYPE: {settings.database_type}")