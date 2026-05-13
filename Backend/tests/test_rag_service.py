from app.services.rag_service import RAGService


def test_rag_returns_relevant_guidelines():
    service = RAGService()

    latest = {
        "temperature": 26.5,
        "humidity": 62
    }

    summary = {
        "hours": 24,
        "count": 10
    }

    docs = service.search(latest, summary)

    assert len(docs) > 0
    assert any(doc["topic"] == "temperature" for doc in docs)
    assert any(doc["topic"] == "humidity" for doc in docs)


def test_rag_documents_have_required_fields():
    service = RAGService()

    latest = {
        "temperature": 22,
        "humidity": 45,
    }

    summary = {
        "hours": 24,
        "count": 10
    }

    docs = service.search(latest, summary)

    for doc in docs:
        assert "id" in doc
        assert "topic" in doc
        assert "content" in doc