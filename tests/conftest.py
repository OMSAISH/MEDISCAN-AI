import asyncio
from backend.app.database.session import engine
from backend.app.database.base import Base
import backend.app.models  # Ensures all models are registered on Base.metadata

def pytest_sessionstart(session):
    """Create all tables at the start of the pytest session."""
    async def _init_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    asyncio.run(_init_db())
