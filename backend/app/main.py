import uuid
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from backend.app.config import settings
from backend.app.database.session import engine, AsyncSessionLocal
from backend.app.database.base import Base
from backend.app.models.user import User, UserRole
from backend.app.auth.password import get_password_hash

# Import API routers
from backend.app.api.auth import router as auth_router
from backend.app.api.drugs import router as drugs_router
from backend.app.api.research import router as research_router
from backend.app.api.evidence import router as evidence_router
from backend.app.api.reports import router as reports_router
from backend.app.api.admin import router as admin_router
from backend.app.api.health import router as health_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("mediscan")

async def init_database():
    """Create database tables and seed initial users if empty."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as db:
        # Check if admin user exists
        stmt = select(User).where(User.email == "admin@mediscan.ai")
        res = await db.execute(stmt)
        if not res.scalar_one_or_none():
            admin_user = User(
                id=str(uuid.uuid4()),
                email="admin@mediscan.ai",
                hashed_password=get_password_hash("Admin12345!"),
                full_name="MediScan Chief Scientist (Admin)",
                role=UserRole.ADMIN,
                organization="MediScan Therapeutics Lab",
                is_active=True,
                is_verified=True
            )
            db.add(admin_user)
            logger.info("Seeded initial admin user: admin@mediscan.ai")

        # Check if demo researcher exists
        stmt2 = select(User).where(User.email == "researcher@mediscan.ai")
        res2 = await db.execute(stmt2)
        if not res2.scalar_one_or_none():
            researcher_user = User(
                id=str(uuid.uuid4()),
                email="researcher@mediscan.ai",
                hashed_password=get_password_hash("Researcher12345!"),
                full_name="Dr. Eleanor Vance",
                role=UserRole.RESEARCHER,
                organization="Biomedical Discovery Institute",
                is_active=True,
                is_verified=True
            )
            db.add(researcher_user)
            logger.info("Seeded initial researcher user: researcher@mediscan.ai")

        await db.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    await init_database()
    yield
    logger.info("Shutting down MediScan AI backend service.")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Drug Repurposing Research Intelligence Platform",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|0\.0\.0\.0|192\.168\.\d+\.\d+|172\.\d+\.\d+\.\d+|10\.\d+\.\d+\.\d+)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers under /api/v1
app.include_router(health_router, prefix=settings.API_V1_PREFIX)
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(drugs_router, prefix=settings.API_V1_PREFIX)
app.include_router(research_router, prefix=settings.API_V1_PREFIX)
app.include_router(evidence_router, prefix=settings.API_V1_PREFIX)
app.include_router(reports_router, prefix=settings.API_V1_PREFIX)
app.include_router(admin_router, prefix=settings.API_V1_PREFIX)

@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "tagline": "AI-Powered Drug Repurposing Research Intelligence",
        "version": settings.APP_VERSION,
        "docs_url": "/docs"
    }
