from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.core.database import get_session
from app.models.sensor_reading import SensorReading
from app.schemas.sensor import SensorReadingCreate
from app.services.measurement_summary_service import MeasurementSummaryService
from app.services.data_quality_service import DataQualityService

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

    if not DataQualityService.is_valid_reading(reading):
        raise HTTPException(
            status_code=422,
            detail="Invalid sensor reading. Measurement was not saved."
        )

    session.add(reading)
    session.commit()
    session.refresh(reading)

    return {"status": "ok", "id": reading.id}


@router.get("/latest")
def get_latest_measurement(session: Session = Depends(get_session)):
    return MeasurementSummaryService.get_latest(session)


@router.get("/history")
def get_measurement_history(
    limit: int = Query(default=100, ge=1, le=500),
    session: Session = Depends(get_session)
):
    return MeasurementSummaryService.get_history(session, limit)


@router.get("/summary")
def get_measurement_summary(
    hours: int = Query(default=24, ge=1, le=168),
    session: Session = Depends(get_session)
):
    return MeasurementSummaryService.get_summary(session, hours)