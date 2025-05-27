from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class TelemetryDataResponse(BaseModel):
    vehicle_id: str
    trip_id: str
    timestamp: datetime
    rpm: Optional[int] = None
    speed: Optional[float] = None
    fuel_consumption: Optional[float] = None
    engine_temp: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class TripAnalysis(BaseModel):
    trip_id: str
    summary: str
    suggestions: List[str]
    eco_score: int
    plain_text: str
    general_advice: Optional[List[str]] = None
    fuel_saved_liters: Optional[float] = None
    co2_avoided_kg: Optional[float] = None


class ReportResponse(BaseModel):
    vehicle_id: str
    score: int
    timestamp: datetime
