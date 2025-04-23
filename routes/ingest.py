from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from models import TelemetryData, TelemetryDataCreate
from db import get_db

router = APIRouter()

@router.post("/ingest")
async def ingest_telemetry_data(
    data: List[TelemetryDataCreate],
    db: Session = Depends(get_db)
):
    try:
        for item in data:
            db_item = TelemetryData(**item.dict())
            db.add(db_item)
        db.commit()
        return {"message": f"{len(data)} données de télémétrie ont été ingérées avec succès"}
    except Exception as e:
        db.rollback()
        raise e 