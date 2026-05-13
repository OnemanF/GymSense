import json

from langchain_ollama import ChatOllama

from app.core.config import settings
from app.ai.tools.gym_tools import (
    get_latest_measurement,
    get_measurement_summary,
    search_gym_environment_guidelines,
)


class GymEnvironmentAgent:
    def __init__(self):
        self.llm = ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_url,
            temperature=0.2,
            format="json",
        )

        self.tools = [
            get_latest_measurement,
            get_measurement_summary,
            search_gym_environment_guidelines,
        ]

    async def generate_assessment(self) -> dict:
        try:
            latest_data = get_latest_measurement.invoke({})
            summary_data = get_measurement_summary.invoke({"hours": 24})
            guideline_data = search_gym_environment_guidelines.invoke({})

            prompt = f"""
You are a gym environment analysis agent.

Your task:
Analyze whether the current gym environment is suitable for training.

You must use:
1. Latest sensor measurement
2. 24 hour measurement summary
3. Retrieved guideline snippets

Focus mainly on temperature and humidity.
Use gas resistance and air quality label as prototype indicators of air quality.
They can support the assessment, but should not be treated as certified air quality measurements.
Do not make severe health claims based only on gas resistance.
If air quality is Poor, recommend ventilation and monitoring rather than describing the gym as dangerous.

Data quality rule:
If temperature is below -10 C, above 60 C, pressure is below 800 hPa, or pressure is above 1100 hPa, treat the data as invalid sensor data.
Do not make health, safety, or emergency claims from invalid sensor data.
If the data is invalid, set riskLevel to "invalid-data" and recommend checking the sensor, wiring, and database readings.

Be realistic and non-alarmist.
Do not say fire, heatstroke, emergency, severe danger, critical danger, or equipment damage.
Temperatures around 20-27 C are not critical.
Humidity slightly above 60 percent may reduce comfort in a gym, but it is not automatically dangerous.

Return valid JSON only with these keys:
- riskLevel: low, moderate, high, or invalid-data
- assessment: short explanation of the current gym environment
- recommendation: practical recommendation for gym users or staff
- usedTools: list of tools used

Latest measurement:
{latest_data}

24h summary:
{summary_data}

Guidelines:
{guideline_data}
"""

            response = await self.llm.ainvoke(prompt)
            content = response.content

            try:
                parsed = json.loads(content)
            except json.JSONDecodeError:
                return self._fallback_response(
                    "The agent response could not be parsed as JSON.",
                    raw=content,
                )

            return self._apply_guardrails(parsed)

        except Exception as e:
            return self._fallback_response(str(e))

    def _apply_guardrails(self, parsed: dict) -> dict:
        risk_level = parsed.get("riskLevel", "moderate")
        assessment = parsed.get("assessment", "No assessment returned.")
        recommendation = parsed.get("recommendation", "No recommendation returned.")
        used_tools = parsed.get("usedTools", [
            "get_latest_measurement",
            "get_measurement_summary",
            "search_gym_environment_guidelines",
        ])

        dangerous_words = [
            "fire",
            "heatstroke",
            "emergency",
            "severe danger",
            "critical danger",
            "equipment damage",
        ]

        lower_assessment = assessment.lower()
        lower_recommendation = recommendation.lower()

        if any(word in lower_assessment for word in dangerous_words) or any(
            word in lower_recommendation for word in dangerous_words
        ):
            risk_level = "moderate"
            assessment = (
                "The gym environment may be less comfortable than ideal, but the current valid sensor data does not support an extreme interpretation."
            )
            recommendation = (
                "Improve ventilation, monitor humidity, and check sensor readings if the values seem unrealistic."
            )

        if risk_level not in ["low", "moderate", "high", "invalid-data"]:
            risk_level = "moderate"

        return {
            "status": "ok",
            "source": "langchain_agent",
            "riskLevel": risk_level,
            "assessment": assessment,
            "recommendation": recommendation,
            "usedTools": used_tools,
        }

    def _fallback_response(self, error: str, raw: str | None = None) -> dict:
        response = {
            "status": "fallback",
            "source": "langchain_agent",
            "riskLevel": "moderate",
            "assessment": (
                "The gym environment could not be fully assessed by the AI agent, but sensor data should still be monitored."
            ),
            "recommendation": (
                "Check ventilation, humidity, and sensor readings manually, then try running the AI assessment again."
            ),
            "usedTools": [],
            "error": error,
        }

        if raw is not None:
            response["raw"] = raw

        return response