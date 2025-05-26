import uuid

from sqlalchemy import Column, String, DateTime, Integer, Float, UUID, Index

from database.engine import Base


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
