from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.core.database import get_session
from app.models.sensor_reading import SensorReading
from app.schemas.sensor import SensorReadingCreate

router = APIRouter(prefix="/api/measurements", tags=["measurements"])


@router.post("")
def create_measurement(
    payload: SensorReadingCreate,
    session: Session = Depends(get_session)
):
    reading = SensorReading(
        device_id=payload.deviceId,
        recorded_at=payload.recordedAt or datetime.now(timezone.utc),
        temperature=payload.temperature,
        humidity=payload.humidity,
        pressure=payload.pressure,
        altitude=payload.altitude,
        light_raw=payload.lightRaw,
        light_percent=payload.lightPercent,
        light_category=payload.lightCategory,
        gas_resistance=payload.gasResistance,
        air_quality_label=payload.airQualityLabel,
        raw_payload=payload.model_dump()
    )

    session.add(reading)
    session.commit()
    session.refresh(reading)

    return {"status": "ok", "id": reading.id}


@router.get("/latest")
def get_latest_measurement(session: Session = Depends(get_session)):
    statement = (
        select(SensorReading)
        .order_by(SensorReading.recorded_at.desc())
        .limit(1)
    )
    return session.exec(statement).first()


@router.get("/history")
def get_measurement_history(limit: int = 100, session: Session = Depends(get_session)):
    statement = (
        select(SensorReading)
        .order_by(SensorReading.recorded_at.desc())
        .limit(limit)
    )
    return session.exec(statement).all()