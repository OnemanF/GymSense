import json
from pathlib import Path


class RAGService:
    def __init__(self):
        file_path = Path(__file__).resolve().parent.parent / "knowledge" / "guidelines"

        with open(file_path, "r", encoding="utf-8-sig") as f:
            self.documents = json.load(f)

    def search(self, latest: dict, summary: dict) -> list[dict]:
        results = []
        seen_ids = set()

        temperature = latest.get("temperature")
        humidity = latest.get("humidity")
        light_category = latest.get("light_category")

        for doc in self.documents:
            topic = doc["topic"]
            include = False

            if topic == "temperature" and temperature is not None:
                include = True
            elif topic == "humidity" and humidity is not None:
                include = True
            elif topic == "light" and light_category is not None:
                include = True
            elif topic == "ventilation" and humidity is not None and humidity > 60:
                include = True

            if include and doc["id"] not in seen_ids:
                results.append(doc)
                seen_ids.add(doc["id"])

        return results[:4]