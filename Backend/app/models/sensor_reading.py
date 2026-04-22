from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB


class SensorReading(SQLModel, table=True):
    __tablename__ = "sensor_readings"

    id: Optional[int] = Field(default=None, primary_key=True)
    device_id: str = Field(index=True)
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)

    temperature: Optional[float] = None
    humidity: Optional[float] = None
    pressure: Optional[float] = None
    altitude: Optional[float] = None

    light_raw: Optional[int] = None
    light_percent: Optional[int] = None
    light_category: Optional[str] = None

    gas_resistance: Optional[float] = None
    air_quality_label: Optional[str] = None

    raw_payload: Optional[dict] = Field(default=None, sa_column=Column(JSONB))