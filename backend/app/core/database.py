from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# Replace postgresql:// with postgresql+asyncpg://
# Move sslmode from URL params to connect_args
raw_url = settings.DATABASE_URL

# Remove ?sslmode=require from URL (asyncpg uses ssl= in connect_args)
if "?sslmode=require" in raw_url:
    raw_url = raw_url.replace("?sslmode=require", "")

async_url = raw_url.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(
    async_url,
    echo=settings.DEBUG,
    future=True,
    connect_args={"ssl": True},  # asyncpg uses ssl=True not sslmode
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()