from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class SensorReadingCreate(BaseModel):
    deviceId: str
    recordedAt: Optional[datetime] = None

    temperature: Optional[float] = None
    humidity: Optional[float] = None
    pressure: Optional[float] = None
    altitude: Optional[float] = None

    gasResistance: Optional[float] = None
    airQualityLabel: Optional[str] = None


class SensorReadingRead(BaseModel):
    id: int
    device_id: str
    recorded_at: datetime

    temperature: Optional[float] = None
    humidity: Optional[float] = None
    pressure: Optional[float] = None
    altitude: Optional[float] = None

    gas_resistance: Optional[float] = None
    air_quality_label: Optional[str] = None

    raw_payload: Optional[dict] = None