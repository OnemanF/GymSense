from app.services.llm_service import LLMService


def test_guardrails_downgrade_extreme_claim_for_normal_temperature():
    service = LLMService()

    parsed = {
        "riskLevel": "high",
        "assessment": "The room is dangerous and critical with fire risk.",
        "recommendation": "Emergency action is needed."
    }

    latest = {
        "temperature": 22.5,
        "humidity": 45
    }

    result = service._apply_guardrails(parsed, latest)

    assert result["riskLevel"] == "moderate"
    assert "dangerous" not in result["assessment"].lower()
    assert "fire" not in result["assessment"].lower()


def test_fallback_normal_conditions_are_low_risk():
    service = LLMService()

    latest = {
        "temperature": 22,
        "humidity": 45
    }

    result = service._fallback_response(latest, "test error")

    assert result["riskLevel"] == "low"
    assert result["status"] == "fallback"