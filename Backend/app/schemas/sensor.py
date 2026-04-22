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

    lightRaw: Optional[int] = None
    lightPercent: Optional[int] = None
    lightCategory: Optional[str] = None

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

    light_raw: Optional[int] = None
    light_percent: Optional[int] = None
    light_category: Optional[str] = None

    gas_resistance: Optional[float] = None
    air_quality_label: Optional[str] = None

    raw_payload: Optional[dict] = None