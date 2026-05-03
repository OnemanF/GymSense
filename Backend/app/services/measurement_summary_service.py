from datetime import datetime, timezone, timedelta
from sqlmodel import Session, select
from app.models.sensor_reading import SensorReading


class MeasurementSummaryService:
    @staticmethod
    def get_latest(session: Session):
        statement = (
            select(SensorReading)
            .order_by(SensorReading.recorded_at.desc())
            .limit(1)
        )
        return session.exec(statement).first()

    @staticmethod
    def get_summary(session: Session, hours: int = 24):
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