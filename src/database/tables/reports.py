import uuid

from sqlalchemy import Column, UUID, String, Integer, Date

from database import Base
from datetime import date


class Report(Base):
    __tablename__ = 'reports'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(String, nullable=False)
    score = Column(Integer, nullable=False)
    date = Column(Date, default=date.today, nullable=False)
