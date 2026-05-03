import json
import requests
from app.core.config import settings


class LLMService:
    def generate_current_assessment(self, latest: dict, summary: dict, context_docs: list[dict]) -> dict:
        schema = {
            "type": "object",
            "properties": {
                "riskLevel": {
                    "type": "string",
                    "enum": ["low", "moderate", "high"]
                },
                "assessment": {
                    "type": "string"
                },
                "recommendation": {
                    "type": "string"
                }
            },
            "required": ["riskLevel", "assessment", "recommendation"]
        }

        context_text = "\n\n".join(
            [f"[{doc['topic']}] {doc['content']}" for doc in context_docs]
        )

        system_prompt = (
            "You are an indoor environment analysis assistant for a room monitoring dashboard. "
            "Your job is to evaluate ordinary indoor comfort conditions based on sensor data and retrieved guidance. "
            "You must be careful, realistic, and non-alarmist. "
            "Do not exaggerate. "
            "Do not mention fire, heatstroke, severe danger, emergency, or equipment damage unless the data is truly extreme. "
            "Temperatures around 20 to 27 C are usually not critical. "
            "Humidity slightly above 60 percent may be uncomfortable, but it is not automatically dangerous. "
            "Low light can be a problem for studying or desk work, but not a safety emergency. "
            "Use the retrieved guidance as supporting context. "
            "Return only valid JSON matching the schema."
        )

        user_prompt = f"""
Latest measurement:
{json.dumps(latest, indent=2)}

24h summary:
{json.dumps(summary, indent=2)}

Retrieved guidance:
{context_text}

Return a realistic indoor-room assessment for a normal person using the room.
JSON schema:
{json.dumps(schema, indent=2)}
"""

        payload = {
            "model": settings.ollama_model,
            "format": "json",
            "stream": False,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        try:
            response = requests.post(
                f"{settings.ollama_url}/api/chat",
                json=payload,
                timeout=60,
            )
            response.raise_for_status()

            data = response.json()

            if "message" not in data or "content" not in data["message"]:
                return self._fallback_response(
                    latest,
                    "The AI service returned an unexpected response format."
                )

            content = data["message"]["content"]

            try:
                parsed = json.loads(content)
            except json.JSONDecodeError:
                return self._fallback_response(
                    latest,
                    "The model response could not be parsed as JSON."
                )

            validated = self._apply_guardrails(parsed, latest)
            validated["status"] = "ok"
            validated["source"] = "llm"
            return validated

        except requests.exceptions.ConnectionError:
            return self._fallback_response(
                latest,
                "Could not connect to Ollama. Make sure Ollama is running locally."
            )

        except requests.exceptions.Timeout:
            return self._fallback_response(
                latest,
                "The Ollama request timed out."
            )

        except requests.exceptions.RequestException as e:
            return self._fallback_response(
                latest,
                f"The AI request failed: {str(e)}"
            )

    def _apply_guardrails(self, parsed: dict, latest: dict) -> dict:
        risk_level = parsed.get("riskLevel", "moderate")
        assessment = parsed.get("assessment", "No assessment returned.")
        recommendation = parsed.get("recommendation", "No recommendation returned.")

        temperature = latest.get("temperature")
        humidity = latest.get("humidity")

        lower_assessment = assessment.lower()
        extreme_words = [
            "fire",
            "heatstroke",
            "severely overheated",
            "dangerous",
            "emergency",
            "equipment damage",
            "critical"
        ]

        looks_extreme = any(word in lower_assessment for word in extreme_words)

        if temperature is not None and 18 <= temperature <= 27:
            if looks_extreme:
                assessment = (
                    "The room appears somewhat warm or uncomfortable. "
                    "The conditions should be interpreted as ordinary indoor comfort issues."
                )
                recommendation = (
                    "Improve ventilation or airflow if the room feels warm. No urgent response is indicated."
                )

            if risk_level == "high":
                risk_level = "moderate"

        if humidity is not None and 30 <= humidity <= 70 and risk_level == "high":
            risk_level = "moderate"

        return {
            "riskLevel": risk_level,
            "assessment": assessment,
            "recommendation": recommendation,
        }

    def _fallback_response(self, latest: dict, error_message: str) -> dict:
        temperature = latest.get("temperature")
        humidity = latest.get("humidity")

        issues = []
        recommendations = []
        risk_level = "low"

        if temperature is not None:
            if temperature < 18:
                issues.append("temperature is somewhat low")
                recommendations.append("Increase room temperature for better comfort.")
                risk_level = "moderate"
            elif temperature > 26:
                issues.append("temperature is somewhat high")
                recommendations.append("Improve airflow or reduce room temperature.")
                risk_level = "moderate"

        if humidity is not None:
            if humidity > 60:
                issues.append("humidity is elevated")
                recommendations.append("Improve ventilation to reduce humidity.")
                risk_level = "moderate"
            elif humidity < 30:
                issues.append("humidity is low")
                recommendations.append("Consider raising humidity for improved comfort.")
                risk_level = "moderate"

        if not issues:
            assessment = "Current room conditions look stable and acceptable."
            recommendation = "No immediate action is needed."
        else:
            assessment = "Current room conditions indicate that " + ", ".join(issues) + "."
            recommendation = " ".join(dict.fromkeys(recommendations))

        return {
            "status": "fallback",
            "source": "rules",
            "riskLevel": risk_level,
            "assessment": assessment,
            "recommendation": recommendation,
            "error": error_message,
        }

