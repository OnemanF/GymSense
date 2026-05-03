import json
from typing import Any

from langchain_core.tools import tool
from sqlmodel import Session

from app.core.database import engine
from app.services.measurement_summary_service import MeasurementSummaryService
from app.services.rag_service import RAGService

def serialize_measurement(reading) -> dict[str, Any] | None:
    if reading is None:
        return None

    return {
        "device_id": reading.device_id,
        "recorded_at": reading.recorded_at.isoformat() if reading.recorded_at else None,
        "temperature": reading.temperature,
        "humidity": reading.humidity,
        "pressure": reading.pressure,
        "altitude": reading.altitude,
        "light_raw": reading.light_raw,
        "light_percent": reading.light_percent,
        "light_category": reading.light_category,
        "gas_resistance": reading.gas_resistance,
        "air_quality_label": reading.air_quality_label,
    }

@tool
def get_latest_measurement() -> str:
    """Gets the latest gym environment measurement from the database."""
    with Session(engine) as session:
        latest = MeasurementSummaryService.get_latest(session)
        return json.dumps(
            {
                "status": "ok",
                "measurement": serialize_measurement(latest),
            },
            indent=2,
        )


@tool
def get_measurement_summary(hours: int = 24) -> str:
    """Gets summary statistics for gym environment measurements over a number of hours."""
    with Session(engine) as session:
        summary = MeasurementSummaryService.get_summary(session, hours=hours)
        return json.dumps(
            {
                "status": "ok",
                "summary": summary,
            },
            indent=2,
        )


@tool
def search_gym_environment_guidelines() -> str:
    """Gets guideline snippets for gym indoor climate, comfort, humidity, temperature and light."""
    rag_service = RAGService()

    fake_latest = {
        "temperature": 22,
        "humidity": 65,
        "light_category": "Low",
    }

    fake_summary = {
        "hours": 24,
        "count": 0,
    }

    docs = rag_service.search(fake_latest, fake_summary)

    return json.dumps(
        {
            "status": "ok",
            "documents": docs,
        },
        indent=2,
    )