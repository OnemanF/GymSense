from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Query
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

@router.get("/summary")
def get_measurement_summary(
    hours: int = Query(default=24, ge=1, le=168),
    session: Session = Depends(get_session)
):
    since = datetime.now(timezone.utc) - timedelta(hours=hours)

    statement = (
        select(SensorReading)
        .where(SensorReading.recorded_at >= since)
        .order_by(SensorReading.recorded_at.asc())
    )

    readings = session.exec(statement).all()

    if not readings:
        return {
            "hours": hours,
            "count": 0,
            "avgTemperature": None,
            "minTemperature": None,
            "maxTemperature": None,
            "avgHumidity": None,
            "minHumidity": None,
            "maxHumidity": None,
            "avgPressure": None,
            "minPressure": None,
            "maxPressure": None,
            "latestLightCategory": None,
        }

    temperatures = [r.temperature for r in readings if r.temperature is not None]
    humidities = [r.humidity for r in readings if r.humidity is not None]
    pressures = [r.pressure for r in readings if r.pressure is not None]

    latest = readings[-1]

    def avg(values):
        return sum(values) / len(values) if values else None

    return {
        "hours": hours,
        "count": len(readings),
        "avgTemperature": avg(temperatures),
        "minTemperature": min(temperatures) if temperatures else None,
        "maxTemperature": max(temperatures) if temperatures else None,
        "avgHumidity": avg(humidities),
        "minHumidity": min(humidities) if humidities else None,
        "maxHumidity": max(humidities) if humidities else None,
        "avgPressure": avg(pressures),
        "minPressure": min(pressures) if pressures else None,
        "maxPressure": max(pressures) if pressures else None,
        "latestLightCategory": latest.light_category,
    }