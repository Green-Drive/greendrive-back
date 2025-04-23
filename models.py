from sqlalchemy import Column, String, Integer, Float, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class TelemetryData(Base):
    __tablename__ = "telemetry_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(String, nullable=False)
    trip_id = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    rpm = Column(Integer)
    speed = Column(Float)
    fuel_consumption = Column(Float)
    engine_temp = Column(Float)
    latitude = Column(Float)
    longitude = Column(Float)

    __table_args__ = (
        Index('idx_trip_timestamp', 'trip_id', 'timestamp'),
    )

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