# app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL connection URL should be in .env file like:
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set. Please add it to your .env file.")

print(f"Database URL configured for: {DATABASE_URL.split('@')[-1]}")

# Create async engine for PostgreSQL
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Shows SQL queries in console (set to False in production)
    pool_size=10,  # Number of connections to keep open
    max_overflow=20,  # Max number of connections that can be created beyond pool_size
    pool_pre_ping=True,  # Verify connections before using them
    pool_recycle=3600,  # Recycle connections after 1 hour
)

# Use async_sessionmaker instead of sessionmaker for async
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()

async def get_db():
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()