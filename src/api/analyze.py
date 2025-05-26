from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from database import Session
from database.tables.telemetry import TelemetryData
from schemas.models import TripAnalysis
from utils.chatgpt import analyze_trip_with_chatgpt


router = APIRouter()


@router.get("/analyze/{trip_id}", response_model=TripAnalysis)
async def analyze_trip(
        trip_id: str,
):
    async with Session() as session:
        stmt = select(TelemetryData).where(TelemetryData.trip_id == trip_id)
        result = await session.execute(stmt)
        trip_data = result.scalars().all()

        if not trip_data:
            raise HTTPException(status_code=404, detail="Trip data not found")

        trip_data_dict = [
            {
                "trip_id": item.trip_id,
                "speed": item.speed,
                "rpm": item.rpm,
                "engine_temp": item.engine_temp,
                "fuel_consumption": item.fuel_consumption,
                "timestamp": item.timestamp
            }
            for item in trip_data
        ]

        return analyze_trip_with_chatgpt(trip_data_dict)
