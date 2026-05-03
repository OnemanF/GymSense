from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.services.langchain_mcp_service import LangChainMCPService

from app.core.database import get_session
from app.services.llm_service import LLMService
from app.services.measurement_summary_service import MeasurementSummaryService
from app.services.rag_service import RAGService
from app.ai.agents.gym_environment_agent import GymEnvironmentAgent

router = APIRouter(prefix="/api/ai", tags=["ai"])


def serialize_latest(latest):
    if latest is None:
        return None

    return {
        "device_id": latest.device_id,
        "recorded_at": latest.recorded_at.isoformat() if latest.recorded_at else None,
        "temperature": latest.temperature,
        "humidity": latest.humidity,
        "pressure": latest.pressure,
        "altitude": latest.altitude,
        "light_raw": latest.light_raw,
        "light_percent": latest.light_percent,
        "light_category": latest.light_category,
        "gas_resistance": latest.gas_resistance,
        "air_quality_label": latest.air_quality_label,
    }


@router.get("/current-assessment")
def get_current_assessment(session: Session = Depends(get_session)):
    latest = MeasurementSummaryService.get_latest(session)
    summary = MeasurementSummaryService.get_summary(session, hours=24)

    if latest is None:
        return {
            "status": "ok",
            "source": "llm",
            "riskLevel": "unknown",
            "assessment": "No sensor data is available yet.",
            "recommendation": "Wait until the device has uploaded measurements.",
        }

    latest_data = serialize_latest(latest)

    rag_service = RAGService()
    context_docs = rag_service.search(latest_data, summary)

    llm_service = LLMService()
    return llm_service.generate_current_assessment(
        latest=latest_data,
        summary=summary,
        context_docs=context_docs,
    )

@router.get("/current-assessment-mcp")
async def get_current_assessment_mcp():
    service = LangChainMCPService()
    return await service.generate_assessment()

@router.get("/gym-agent-assessment")
async def get_gym_agent_assessment():
    agent = GymEnvironmentAgent()
    return await agent.generate_assessment()