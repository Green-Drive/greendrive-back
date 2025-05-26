from sqlalchemy import Column, String, Integer, Float, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

from pydantic import BaseModel
from typing import List, Optional


class TelemetryDataCreate(BaseModel):
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
