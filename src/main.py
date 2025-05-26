from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from api import analyze, ingest
from database.engine import init_db


load_dotenv()


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        print("Initializing database...")
        await init_db()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Failed to initialize database: {e}")
        raise RuntimeError(f"Database initialization failed: {e}")
    yield
    print("Shutting down application...")


app = FastAPI(
    title="Vehicle Telemetry API",
    description="API for vehicle telemetry data ingestion and analysis",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(ingest.router, prefix="/api/v1", tags=["Ingestion"])
app.include_router(analyze.router, prefix="/api/v1", tags=["Analysis"])
