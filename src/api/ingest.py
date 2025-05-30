from typing import List

from fastapi import APIRouter

from database import Session
from schemas.models import TelemetryDataResponse
from . import TelemetryData


router = APIRouter()


@router.post("/ingest")
async def ingest_telemetry_data(
        data: List[TelemetryDataResponse]
):
    async with Session() as session:
        try:
            for item in data:
                db_item = TelemetryData(**item.dict())
                session.add(db_item)
            await session.commit()
            return {"message": f"{len(data)} données de télémétrie ont été ingérées avec succès"}
        except Exception as e:
            await session.rollback()
            raise e
