from datetime import datetime, timezone, timedelta
from sqlmodel import Session, select

from app.models.sensor_reading import SensorReading
from app.services.data_quality_service import DataQualityService


class MeasurementSummaryService:
    @staticmethod
    def get_latest(session: Session):
        statement = (
            select(SensorReading)
            .order_by(SensorReading.recorded_at.desc())
            .limit(20)
        )

        readings = session.exec(statement).all()

        for reading in readings:
            if DataQualityService.is_valid_reading(reading):
                return reading

        return None

    @staticmethod
    def get_history(session: Session, limit: int = 100):
        statement = (
            select(SensorReading)
            .order_by(SensorReading.recorded_at.desc())
            .limit(limit * 3)
        )

        readings = session.exec(statement).all()

        valid_readings = [
            reading for reading in readings
            if DataQualityService.is_valid_reading(reading)
        ]

        return valid_readings[:limit]

    @staticmethod
    def get_summary(session: Session, hours: int = 24):
        since = datetime.now(timezone.utc) - timedelta(hours=hours)

        statement = (
            select(SensorReading)
            .where(SensorReading.recorded_at >= since)
            .order_by(SensorReading.recorded_at.asc())
        )

        readings = session.exec(statement).all()

        readings = [
            reading for reading in readings
            if DataQualityService.is_valid_reading(reading)
        ]

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
                "avgGasResistance": None,
                "minGasResistance": None,
                "maxGasResistance": None,
                "latestAirQualityLabel": None,
            }

        temperatures = [r.temperature for r in readings if r.temperature is not None]
        humidities = [r.humidity for r in readings if r.humidity is not None]
        pressures = [r.pressure for r in readings if r.pressure is not None]
        gas_resistances = [
            r.gas_resistance for r in readings
            if r.gas_resistance is not None
        ]

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
            "avgGasResistance": avg(gas_resistances),
            "minGasResistance": min(gas_resistances) if gas_resistances else None,
            "maxGasResistance": max(gas_resistances) if gas_resistances else None,
            "latestAirQualityLabel": latest.air_quality_label,
        }