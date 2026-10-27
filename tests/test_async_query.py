"""Tests for synchronous /query endpoint."""

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app


def test_query_returns_direct_answer():
    """/query should run the pipeline synchronously and return the answer."""
    mock_state = {
        "final_answer": "hello",
        "plan": ["Intent: Technical", "Search Term: hi"],
        "status": "Response generated.",
        "documents": ["doc1"],
    }
    mock_agent = MagicMock()
    mock_agent.invoke.return_value = mock_state

    # Ensure rag_agent exists on app.state before TestClient uses it.
    app.state.rag_agent = mock_agent

    client = TestClient(app)
    with patch("app.main.guard") as mock_guard:
        mock_guard.return_value = (False, "")
        response = client.post("/query", json={"q": "hi", "thread_id": "t1"})

    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "hello"
    assert data["status"] == "Response generated."
    assert data["sources"] == ["doc1"]
    assert data["thread_id"] == "t1"
    mock_agent.invoke.assert_called_once()


def test_query_blocks_guardrails():
    """/query should return a blocked response when guardrails fire."""
    client = TestClient(app)
    with patch("app.main.guard") as mock_guard:
        mock_guard.return_value = (True, "Blocked message")
        response = client.post("/query", json={"q": "bad prompt", "thread_id": "t2"})

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Blocked by guardrails."
    assert data["answer"] == "Blocked message"


def test_omitted_thread_id_is_not_shared_default():
    """Omitting thread_id must not join the old shared default_user thread."""
    client = TestClient(app)
    with patch("app.main.guard") as mock_guard:
        mock_guard.return_value = (True, "blocked")
        response = client.post("/query", json={"q": "hi"})

    assert response.status_code == 200
    assert response.json()["thread_id"] != "default_user"
    assert response.json()["thread_id"]


def test_query_rejects_invalid_thread_id_and_empty_question():
    client = TestClient(app)
    invalid_thread = client.post("/query", json={"q": "hi", "thread_id": "not valid"})
    empty_question = client.post("/query", json={"q": ""})
    assert invalid_thread.status_code == 422
    assert empty_question.status_code == 422
