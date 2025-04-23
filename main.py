from fastapi import FastAPI
from routes import ingest, analyze
from db import init_db

app = FastAPI(
    title="API de Télémétrie Véhiculaire",
    description="API pour l'ingestion et l'analyse des données de télémétrie véhiculaire",
    version="1.0.0"
)

# Initialiser la base de données
init_db()

# Inclure les routes
app.include_router(ingest.router, prefix="/api/v1", tags=["ingestion"])
app.include_router(analyze.router, prefix="/api/v1", tags=["analyse"])

@app.get("/")
async def root():
    return {"message": "API de Télémétrie Véhiculaire - Documentation disponible sur /docs"}