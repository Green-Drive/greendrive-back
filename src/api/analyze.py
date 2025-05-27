from fastapi import APIRouter, HTTPException
from sqlalchemy import select
import json

from database import Session
from database.tables.reports import Report
from database.tables.telemetry import TelemetryData
from schemas import ReportResponse
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
        print(trip_data[0].vehicle_id)
        if not trip_data:
            raise HTTPException(status_code=404, detail="Trip data not found")

        trip_data_dict = [
            {
                "vehicle_id": item.vehicle_id,
                "trip_id": item.trip_id,
                "speed": item.speed,
                "rpm": item.rpm,
                "engine_temp": item.engine_temp,
                "fuel_consumption": item.fuel_consumption,
                "timestamp": item.timestamp,
            }
            for item in trip_data
        ]

        report = analyze_trip_with_chatgpt(trip_data_dict)
        if not report:
            raise HTTPException(status_code=500, detail="Failed to analyze trip data")

        db_report = Report(
            vehicle_id=trip_data[0].vehicle_id,
            score=report.eco_score,
            analysis=json.dumps(report.model_dump())
        )
        session.add(db_report)
        await session.commit()

        return report


@router.get("/reports/{vehicle_id}", response_model=list[ReportResponse])
async def get_reports(
        vehicle_id: str,
):
    async with Session() as session:
        stmt = select(Report).where(Report.vehicle_id == vehicle_id)
        result = await session.execute(stmt)
        reports = result.scalars().all()

        if not reports:
            raise HTTPException(status_code=404, detail="No reports found for this vehicle")

        return [ReportResponse(
            vehicle_id=report.vehicle_id,
            score=report.score,
            timestamp=report.date,
            analysis=report.analysis,
        ) for report in reports]
