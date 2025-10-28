from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.routes import sessions, health
from app.services.browser_manager import browser_manager
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown."""
    # Startup
    print("🦈 Starting SharkBrowser API...")
    print(f"📊 Max browsers: {settings.max_browsers}")
    print(f"🔌 Port range: {settings.port_start}-{settings.port_end}")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down SharkBrowser API...")
    await browser_manager.cleanup_all()


# Create FastAPI application
app = FastAPI(
    title="SharkBrowser API",
    description="Docker-based browser automation API for EC2 deployment",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware for Postman access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(sessions.router)
app.include_router(health.router)


@app.get("/")
async def root():
    """Root endpoint with basic API information."""
    return {
        "message": "🦈 SharkBrowser API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "sessions": "/v1/sessions",
        "example": "POST /v1/sessions to create a browser and get WebSocket URL"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.env == "development"
    )