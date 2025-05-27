import os
from pathlib import Path
from typing import Optional

from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import declarative_base


def _find_project_root() -> Optional[Path]:
    """
    Find the project root by looking for .env file.
    """
    current = Path.cwd()
    while current != current.parent:
        if (current / ".env").exists():
            return current
        current = current.parent
    return None


def _load_env_from_project_root() -> None:
    """
    Load environment variables from .env file in project root.
    """
    project_root = _find_project_root()
    if not project_root:
        return

    env_file = project_root / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()


def _get_database_url() -> str:
    """
    Build the database URL from environment variables.
    Raises RuntimeError if required vars are missing.
    """
    _load_env_from_project_root()

    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db_name = os.getenv("POSTGRES_DB")

    if not all([user, password, db_name]):
        raise RuntimeError(
            "Missing database configuration. Please provide configuration through:\n"
            "1. .env file in project root\n"
            "2. Environment variables"
        )

    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}"


def _create_engine_and_session() -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
    """
    Ensure database exists, then create and return SQLAlchemy Engine and Session factory.
    """
    db_url = _get_database_url()

    engine = create_async_engine(
        db_url,
        pool_size=10,
        max_overflow=20,
        echo=False,
        future=True,
    )
    sm = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )
    return engine, sm



Base = declarative_base()
Engine, Session = _create_engine_and_session()


async def init_db() -> None:
    """
    Initialize the database connection.
    Configuration will be loaded from:
    1. .env file in project root
    2. Environment variables
    """
    global Engine, Session
    Engine, Session = _create_engine_and_session()

    async with Engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
