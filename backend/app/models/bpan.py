from app.core.database import Base
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone


class BPAN(Base):
    __tablename__ = "bpans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code_21char = Column(String(21), unique=True, nullable=False, index=True)
    model_id = Column(UUID(as_uuid=True), ForeignKey("battery_models.id"), nullable=False)
    year_code = Column(String(1), ForeignKey("manufacturing_years.code"), nullable=False)
    month_code = Column(String(1), ForeignKey("manufacturing_months.code"), nullable=False)
    date_code = Column(String(1), ForeignKey("manufacturing_dates.code"), nullable=False)
    serial_number = Column(Integer, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    model = relationship("BatteryModel", back_populates="bpans")
    creator = relationship("User", back_populates="bpans")
    year = relationship("ManufacturingYear")
    month = relationship("ManufacturingMonth")
    date = relationship("ManufacturingDate")


class SystemConfig(Base):
    __tablename__ = "system_config"

    key = Column(String(50), primary_key=True)
    value = Column(Text)
