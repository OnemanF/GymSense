import sys
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP
from sqlmodel import Session

BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(BACKEND_ROOT))

from app.core.database import engine
from app.services.measurement_summary_service import MeasurementSummaryService
from app.services.rag_service import RAGService

mcp = FastMCP("gymsense")


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
        "gas_resistance": reading.gas_resistance,
        "air_quality_label": reading.air_quality_label,
    }


@mcp.tool()
def get_latest_measurement() -> dict[str, Any]:
    """Get the latest Gymsense sensor measurement."""
    with Session(engine) as session:
        latest = MeasurementSummaryService.get_latest(session)
        return {"status": "ok", "measurement": serialize_measurement(latest)}


@mcp.tool()
def get_measurement_summary(hours: int = 24) -> dict[str, Any]:
    """Get summary statistics for Gymsense sensor data."""
    with Session(engine) as session:
        summary = MeasurementSummaryService.get_summary(session, hours=hours)
        return {"status": "ok", "summary": summary}


@mcp.tool()
def search_guidelines() -> dict[str, Any]:
    """Retrieve indoor climate guideline snippets for RAG grounding."""
    rag_service = RAGService()

    fake_latest = {
        "temperature": 22,
        "humidity": 65,
        "gas_resistance": 15000,
        "air_quality_label": "Poor",
    }

    fake_summary = {
        "hours": 24,
        "count": 0,
    }

    docs = rag_service.search(fake_latest, fake_summary)

    return {"status": "ok", "documents": docs}


if __name__ == "__main__":
    mcp.run()