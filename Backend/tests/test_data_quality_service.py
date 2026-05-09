from types import SimpleNamespace

from app.services.data_quality_service import DataQualityService


def test_valid_reading_is_accepted():
    reading = SimpleNamespace(
        temperature=22.5,
        humidity=45.0,
        pressure=1024.0
    )

    assert DataQualityService.is_valid_reading(reading) is True


def test_extreme_temperature_is_rejected():
    reading = SimpleNamespace(
        temperature=182.0,
        humidity=45.0,
        pressure=1024.0
    )

    assert DataQualityService.is_valid_reading(reading) is False


def test_invalid_pressure_is_rejected():
    reading = SimpleNamespace(
        temperature=22.0,
        humidity=45.0,
        pressure=-172.0
    )

    assert DataQualityService.is_valid_reading(reading) is False