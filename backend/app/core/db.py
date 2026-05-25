import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

load_dotenv()

# We need an async connection for FastAPI
# Using asyncpg: postgresql+asyncpg://user:password@host:port/dbname
DATABASE_URL = os.getenv("SUPABASE_DB_URL", "")

engine = create_async_engine(DATABASE_URL, echo=True, future=True)

async def init_db():
    # In production, we'd use Alembic. For this setup, we assume 
    # supabase_schema.sql was run manually to set up tables and pgvector.
    pass

async def get_session() -> AsyncSession:
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
