import json
import sys
from pathlib import Path

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_ollama import ChatOllama

from app.core.config import settings


class LangChainMCPService:
    async def generate_assessment(self) -> dict:
        backend_root = Path(__file__).resolve().parent.parent.parent
        mcp_server_path = backend_root / "mcp_server" / "server.py"

        client = MultiServerMCPClient(
            {
                "gymsense": {
                    "command": sys.executable,
                    "args": [str(mcp_server_path)],
                    "transport": "stdio",
                }
            }
        )

        tools = await client.get_tools()

        latest_tool = self._find_tool(tools, "get_latest_measurement")
        summary_tool = self._find_tool(tools, "get_measurement_summary")
        guidelines_tool = self._find_tool(tools, "search_guidelines")

        latest_result = await latest_tool.ainvoke({})
        summary_result = await summary_tool.ainvoke({"hours": 24})
        guidelines_result = await guidelines_tool.ainvoke({})

        llm = ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_url,
            temperature=0.2,
            format="json",
        )

        prompt = f"""
You are an indoor climate analysis assistant.

Use ONLY the provided sensor data, summary statistics, and retrieved guideline snippets.

Be realistic and non-alarmist.
Do not mention fire, heatstroke, emergency, severe danger, or equipment damage unless values are truly extreme.
Temperatures around 20-27 C are not critical.
Humidity slightly above 60 percent may be uncomfortable but is not automatically dangerous.

Use gas resistance and air quality label as prototype indicators of air quality.
Higher gas resistance usually suggests cleaner air, while lower gas resistance may suggest poorer air quality.
Do not treat gas resistance as a certified air quality measurement.
If air quality is Poor, recommend ventilation and monitoring rather than making severe health claims.

Return valid JSON only with:
- riskLevel: low, moderate, or high
- assessment: short but useful explanation
- recommendation: practical user action

Latest measurement:
{json.dumps(latest_result, indent=2)}

24h summary:
{json.dumps(summary_result, indent=2)}

Retrieved guidelines:
{json.dumps(guidelines_result, indent=2)}
"""

        response = await llm.ainvoke(prompt)
        content = response.content

        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            return {
                "status": "fallback",
                "source": "langchain_mcp",
                "riskLevel": "moderate",
                "assessment": "The AI response could not be parsed as JSON.",
                "recommendation": "Try again or use the rule-based fallback.",
                "raw": content,
            }

        return {
            "status": "ok",
            "source": "langchain_mcp",
            "riskLevel": parsed.get("riskLevel", "moderate"),
            "assessment": parsed.get("assessment", "No assessment returned."),
            "recommendation": parsed.get("recommendation", "No recommendation returned."),
        }

    def _find_tool(self, tools, name: str):
        for tool in tools:
            if tool.name == name or tool.name.endswith(name):
                return tool

        available = [tool.name for tool in tools]
        raise ValueError(f"Tool '{name}' not found. Available tools: {available}")